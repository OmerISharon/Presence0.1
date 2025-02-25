import re, json, shutil, random
from pathlib import Path
from datetime import datetime
from moviepy import VideoClip, AudioFileClip, CompositeAudioClip 
from PIL import Image, ImageDraw, ImageFont
from config import *  # uses variables: DIR_OFFLINE_TEXT, DIR_OFFLINE_TEXT_ARCHIVE, OUT_BASE_FOLDER, FONT_PATH, FONT_SIZE, TYPING_SOUNDS_DIR, FPS
import numpy as np

def compute_timestamps(text, base_delay, variation_range):
    """
    Compute per-character delays with random variation.
    Returns:
      - timestamps: list of cumulative delays for each character.
      - total_duration: total time required.
    """
    timestamps = []
    cumulative = 0
    for char in text:
        delay = base_delay * random.uniform(*variation_range)
        cumulative += delay
        timestamps.append(cumulative)
    return timestamps, cumulative

def build_timeline(sentences, base_delay, initial_pause, gap_pause):
    """
    Build the timeline for typing and (if applicable) backspacing.
    For each sentence (except the final one), backspacing events are computed.
    Returns a list of timeline segments and the total duration.
    """
    timeline = []
    current_time = initial_pause
    for i, item in enumerate(sentences):
        text = item['text']
        pause_time = item['delay']
        # Compute human-like typing timestamps with a variation (80%-120% of base delay)
        typing_timestamps, type_duration = compute_timestamps(text, base_delay, (0.8, 1.2))
        # For non-final sentences, compute backspacing timestamps (base_delay/2 for 2x faster)
        if i < len(sentences) - 1:
            back_timestamps, back_duration = compute_timestamps(text, base_delay/2, (0.7, 1.0))
        else:
            back_timestamps, back_duration = [], 0

        segment = {
            'sentence': text,
            'start_typing': current_time,
            'typing_timestamps': typing_timestamps,
            'end_typing': current_time + type_duration,
            'pause': pause_time,
            'start_back': current_time + type_duration + pause_time,
            'backspacing_timestamps': back_timestamps,
            'end_back': current_time + type_duration + pause_time + back_duration,
        }
        timeline.append(segment)

        # Update current_time for next segment.
        if i < len(sentences) - 1:
            current_time += type_duration + pause_time + back_duration + gap_pause
        else:
            # For the final sentence, ensure the pause is at least 3 seconds.
            final_pause = max(pause_time, 3)
            current_time += type_duration + final_pause
    return timeline, current_time

def create_audio_events(timeline, base_delay):
    """
    Create a list of audio events for typing and backspacing.
    For a less intense sound, we trigger a sound for every second character.
    """
    typing_audio_dir = Path(TYPING_SOUNDS_DIR)
    audio_files = list(typing_audio_dir.glob("*.mp3"))
    def get_random_sound():
        return random.choice(audio_files)
    
    audio_events = []
    # Typing sound events
    for segment in timeline:
        sentence = segment['sentence']
        # For every second character
        for i in range(0, len(sentence), 2):
            # Use the computed per-character timestamp for more natural timing
            event_time = segment['start_typing'] + segment['typing_timestamps'][i]
            sound_file = get_random_sound()
            sound_clip_full = AudioFileClip(str(sound_file))
            # Use a duration equal to base_delay (or the clip's duration, whichever is shorter)
            clip_duration = min(base_delay, sound_clip_full.duration)
            sound_clip = sound_clip_full.subclipped(0, clip_duration).with_start(event_time)
            audio_events.append(sound_clip)
        # Backspacing sound events (if applicable)
        if segment['backspacing_timestamps']:
            for i in range(0, len(sentence), 2):
                event_time = segment['start_back'] + segment['backspacing_timestamps'][i]
                sound_file = get_random_sound()
                sound_clip_full = AudioFileClip(str(sound_file))
                clip_duration = min(base_delay, sound_clip_full.duration)
                sound_clip = sound_clip_full.subclipped(0, clip_duration).with_start(event_time)
                audio_events.append(sound_clip)
    return audio_events

def make_frame(t, timeline, const_y, width):
    """
    Render the frame at time t using the timeline.
    The vertical position (y) is fixed to the constant value computed from the font metrics.
    """
    # Create a blank image (black background)
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    displayed_text = ""
    
    # Determine which timeline segment applies
    for i, segment in enumerate(timeline):
        if t < segment['start_typing']:
            # Not reached this sentence yet.
            break
        elif segment['start_typing'] <= t < segment['end_typing']:
            # Typing in progress
            offset = t - segment['start_typing']
            num_chars = sum(1 for ts in segment['typing_timestamps'] if ts <= offset)
            displayed_text = segment['sentence'][:num_chars]
            break
        elif segment['end_typing'] <= t < segment['start_back']:
            # Finished typing, holding full sentence
            displayed_text = segment['sentence']
            break
        elif segment['backspacing_timestamps'] and segment['start_back'] <= t < segment['end_back']:
            # Backspacing in progress
            offset = t - segment['start_back']
            num_chars_removed = sum(1 for ts in segment['backspacing_timestamps'] if ts <= offset)
            remaining_chars = len(segment['sentence']) - num_chars_removed
            displayed_text = segment['sentence'][:remaining_chars]
            break
        elif t >= segment['end_back']:
            # After backspacing for non-final sentences, show nothing
            if i < len(timeline) - 1:
                displayed_text = ""
            else:
                displayed_text = segment['sentence']
    # Center horizontally using the current text width, but use constant y position
    if displayed_text:
        bbox = draw.textbbox((0, 0), displayed_text, font=font)
        text_width = bbox[2] - bbox[0]
    else:
        text_width = 0
    x = (width - text_width) / 2
    draw.text((x, const_y), displayed_text, font=font, fill='red')
    return np.array(img)

def main():
    # --- 1. File handling: find the oldest txt file ---
    input_dir = Path(DIR_OFFLINE_TEXT)
    archive_dir = Path(DIR_OFFLINE_TEXT_ARCHIVE)
    output_dir = Path(OUT_BASE_FOLDER)
    
    txt_files = sorted(input_dir.glob("*.txt"), key=lambda f: f.stat().st_ctime)
    if not txt_files:
        raise FileNotFoundError("No txt file found in input directory")
    txt_file = txt_files[0]
    
    # --- 2. Parse the text file for sentences and delays ---
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
    
    # --- 3. Video parameters ---
    global width, height, font  # used in make_frame below
    width, height = 1080, 1920
    font_path = Path(FONT_PATH)
    font_size = int(FONT_SIZE)
    font = ImageFont.truetype(str(font_path), font_size)
    # Fix the vertical centering using font metrics (so y remains constant)
    ascent, descent = font.getmetrics()
    const_y = (height - (ascent + descent)) / 2

    # Typing animation parameters
    base_char_time = 0.05  # base delay per character
    initial_pause = 1
    gap_pause = 1

    # --- 4. Build timeline ---
    timeline, total_duration = build_timeline(sentences, base_char_time, initial_pause, gap_pause)
    
    # --- 5. Audio integration ---
    audio_events = create_audio_events(timeline, base_char_time)
    composite_audio = CompositeAudioClip(audio_events)
    
    # --- 6. Create video clip ---
    clip = VideoClip(lambda t: make_frame(t, timeline, const_y, width), duration=total_duration)
    clip = clip.with_fps(FPS)
    clip = clip.with_audio(composite_audio)
    
    # --- 7. Write video output ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = output_dir / timestamp
    output_folder.mkdir(parents=True, exist_ok=True)
    video_output_path = output_folder / f"{timestamp}.mp4"
    clip.write_videofile(str(video_output_path))
    
    # --- 8. Save metadata as JSON ---
    metadata = {
        "title": sentences[0]['text'],
        "description": ". ".join([s['text'] for s in sentences]),
        "creation_timestamp": timestamp,
    }
    with open(output_folder / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    
    # --- 9. Move processed txt file to archive ---
    shutil.move(str(txt_file), str(archive_dir / txt_file.name))

if __name__ == '__main__':
    main()
