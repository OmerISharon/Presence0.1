import re, json, shutil, random
from pathlib import Path
from datetime import datetime
from moviepy import VideoClip, AudioFileClip, CompositeAudioClip 
from PIL import Image, ImageDraw, ImageFont
from config import *  # uses variables: DIR_OFFLINE_TEXT, DIR_OFFLINE_TEXT_ARCHIVE, OUT_BASE_FOLDER, FONT_PATH, FONT_SIZE, TYPING_SOUNDS_DIR, FPS
import numpy as np

# New fade out duration (in seconds)
FADE_OUT_DURATION = 1.0

def compute_timestamps(text, base_delay, variation_range):
    """
    Compute per-character delays with random variation.
    Adds extra delay for punctuation and spaces to simulate human typing.
    Returns:
      - timestamps: list of cumulative delays for each character.
      - total_duration: total time required.
    """
    timestamps = []
    cumulative = 0
    for char in text:
        delay = base_delay * random.uniform(*variation_range)
        if char in ".!?":
            delay *= random.uniform(1.5, 2.0)
        elif char == " ":
            delay *= random.uniform(1.2, 1.5)
        cumulative += delay
        timestamps.append(cumulative)
    return timestamps, cumulative

def build_timeline(sentences, base_delay, initial_pause, gap_pause, fade_duration):
    """
    Build the timeline for typing and fade out.
    For each sentence (except the final one), a fade-out event is computed.
    Returns a list of timeline segments and the total duration.
    """
    timeline = []
    current_time = initial_pause
    for i, item in enumerate(sentences):
        text = item['text']
        pause_time = item['delay']
        # Use a very tight variation range for smooth, consistent timing.
        typing_timestamps, type_duration = compute_timestamps(text, base_delay, (0.98, 1.02))
        segment = {
            'sentence': text,
            'start_typing': current_time,
            'typing_timestamps': typing_timestamps,
            'end_typing': current_time + type_duration,
            'pause': pause_time,
        }
        if i < len(sentences) - 1:
            segment['start_fade'] = current_time + type_duration + pause_time
            segment['fade_duration'] = fade_duration
            segment['end_fade'] = segment['start_fade'] + fade_duration
        timeline.append(segment)
        if i < len(sentences) - 1:
            current_time += type_duration + pause_time + fade_duration + gap_pause
        else:
            final_pause = max(pause_time, 3)
            current_time += type_duration + final_pause
    return timeline, current_time

def create_audio_events(timeline, base_delay):
    """
    Create a list of audio events for typing sounds.
    For a less intense sound, we trigger a sound for every second character.
    (Fade-out has no associated sound.)
    """
    typing_audio_dir = Path(TYPING_SOUNDS_DIR)
    audio_files = list(typing_audio_dir.glob("*.mp3"))
    def get_random_sound():
        return random.choice(audio_files)
    
    audio_events = []
    for segment in timeline:
        sentence = segment['sentence']
        for i in range(0, len(sentence), 2):
            event_time = segment['start_typing'] + segment['typing_timestamps'][i]
            sound_file = get_random_sound()
            sound_clip_full = AudioFileClip(str(sound_file))
            clip_duration = min(base_delay, sound_clip_full.duration)
            sound_clip = sound_clip_full.subclipped(0, clip_duration).with_start(event_time)
            audio_events.append(sound_clip)
    return audio_events

def wrap_text(text, font, draw, max_width):
    """
    Break text into multiple lines so that each line fits within max_width.
    """
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = word if not current_line else current_line + " " + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def make_frame(t, timeline, const_y, width):
    """
    Render the frame at time t using the timeline.
    Instead of re-centering partial text on every frame, we pre-calculate
    the final wrapped lines and their left margins (for centering). Then we
    reveal the text progressively over those fixed positions.
    """
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Determine which timeline segment applies and the current state.
    selected_segment = None
    branch = None  # "typing", "hold", or "fade"
    fade_factor = 1.0
    progress = 0
    for segment in timeline:
        if t < segment['start_typing']:
            break  # Not reached this sentence yet.
        elif segment['start_typing'] <= t < segment['end_typing']:
            selected_segment = segment
            branch = "typing"
            progress = (t - segment['start_typing']) / (segment['end_typing'] - segment['start_typing'])
        elif t < segment.get('start_fade', float('inf')):
            selected_segment = segment
            branch = "hold"
        elif 'start_fade' in segment and segment['start_fade'] <= t < segment['end_fade']:
            selected_segment = segment
            branch = "fade"
            fade_factor = 1 - ((t - segment['start_fade']) / segment['fade_duration'])
        elif t >= segment.get('end_fade', segment['end_typing']):
            if timeline.index(segment) < len(timeline) - 1:
                selected_segment = segment
                branch = "none"
            else:
                selected_segment = segment
                branch = "hold"
    if not selected_segment or branch == "none":
        return np.array(img)
    
    full_text = selected_segment['sentence']
    max_text_width = int(width * 0.9)
    final_lines = wrap_text(full_text, font, draw, max_text_width)
    
    # Compute vertical metrics.
    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    total_text_height = line_height * len(final_lines)
    y_start = (height - total_text_height) / 2
    
    # Determine how many characters to reveal.
    if branch == "typing":
        revealed_count = int(progress * len(full_text))
    else:
        revealed_count = len(full_text)
    
    # Distribute revealed characters over the final wrapped lines.
    remaining = revealed_count
    drawn_lines = []
    for line in final_lines:
        if remaining >= len(line):
            drawn_lines.append(line)
            remaining -= len(line)
        else:
            drawn_lines.append(line[:remaining])
            remaining = 0

    # Draw each line at its fixed left margin (computed from full line width).
    for i, line in enumerate(final_lines):
        bbox_full = draw.textbbox((0, 0), line, font=font)
        full_line_width = bbox_full[2] - bbox_full[0]
        left_x = (width - full_line_width) / 2
        y = y_start + i * line_height
        text_to_draw = drawn_lines[i] if i < len(drawn_lines) else ""
        if branch == "fade":
            text_color = (int(255 * fade_factor), 0, 0)
        else:
            text_color = (255, 0, 0)
        draw.text((left_x, y), text_to_draw, font=font, fill=text_color)
    
    # The blinking caret has been removed.
    
    return np.array(img)


def main():
    # --- 1. File handling: choose the lowest-numbered txt file ---
    input_dir = Path(DIR_OFFLINE_TEXT)
    archive_dir = Path(DIR_OFFLINE_TEXT_ARCHIVE)
    output_dir = Path(OUT_BASE_FOLDER)
    
    txt_files = sorted(input_dir.glob("*.txt"), key=lambda f: int(f.stem) if f.stem.isdigit() else float('inf'))
    if not txt_files:
        raise FileNotFoundError("No txt file found in input directory")
    txt_file = txt_files[0]
    
    # --- 2. Initialize video parameters ---
    global width, height, font  # used in make_frame below
    width, height = 1080, 1920
    font_path = Path(FONT_PATH)
    font_size = int(FONT_SIZE)
    font = ImageFont.truetype(str(font_path), font_size)
    const_y = None  # Not used because we center the text block.
    
    # Typing animation parameters
    base_char_time = 0.05  # Adjust this for slower typing if needed.
    initial_pause = 1
    gap_pause = 1

    # --- 3. Parse the text file for sentences and delays ---
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
    
    sentences = []
    for line in lines:
        match = re.search(r'\[(\d+)\]$', line)
        if match:
            delay = int(match.group(1))
            sentence = line[:match.start()].strip().strip('"')
        else:
            delay = 5
            sentence = line.strip().strip('"')
        sentences.append({'text': sentence, 'delay': delay})
    
    # --- 4. Build timeline ---
    timeline, total_duration = build_timeline(sentences, base_char_time, initial_pause, gap_pause, FADE_OUT_DURATION)
    
    # --- 5. Audio integration ---
    audio_events = create_audio_events(timeline, base_char_time)
    composite_audio = CompositeAudioClip(audio_events)
    
    # --- 6. Create video clip ---
    clip = VideoClip(lambda t: make_frame(t, timeline, const_y, width), duration=total_duration)
    clip = clip.with_fps(FPS)  # Using FPS from your config.
    clip = clip.with_audio(composite_audio)
    
    # --- 7. Write video output ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = output_dir / f"{txt_file.stem}_{timestamp}"
    output_folder.mkdir(parents=True, exist_ok=True)
    video_output_path = output_folder / f"{txt_file.stem}_{timestamp}.mp4"
    clip.write_videofile(str(video_output_path))
    
    # --- 8. Save metadata as JSON ---
    metadata = {
        "title": sentences[0]['text'] if sentences else "",
        "description": ". ".join([s['text'] for s in sentences]),
        "creation_timestamp": timestamp,
    }
    with open(output_folder / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    
    # --- 9. Move processed txt file to archive ---
    shutil.move(str(txt_file), str(archive_dir / txt_file.name))

if __name__ == '__main__':
    main()
