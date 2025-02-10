import os
import cv2
import glob
import json
import shutil
import random
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from datetime import datetime

# -----------------------------------------------------------------
# Configuration Variables
# -----------------------------------------------------------------

OPENAI_API_KEY_PATH = "C:\\Presence\\GlobalResources\\OPENAI_API_KEY.txt"
OPENAI_API_KEY = "OPENAI_API_KEY"

DEBUG_MODE = True
DEBUG_TEXT = "Hello from Debug Mode!"

ROOT_DIR = "C:\\Presence\\Presence0.1\\Creator\\GodModeNotes"

DIR_OFFLINE_TEXT = f"{ROOT_DIR}\\Resources\\Text"
DIR_OFFLINE_TEXT_ARCHIVE = f"{ROOT_DIR}\\Resources\\Text - Archive"
PATH_PROMPT = f"{ROOT_DIR}\\Resources\\Prompt\\Main_Prompt.txt"

INCLUDE_TYPING_SOUNDS = True
TYPING_SOUNDS_DIR = f"{ROOT_DIR}\\Resources\\Audio\\Typing_Audio"
BACKGROUND_AUDIO = f"{ROOT_DIR}\\Resources\\Audio\\Background_Audio\\Root\\v1\\Full Audio.mp3"

OUT_BASE_FOLDER = f"{ROOT_DIR}\\Debug_Output" if DEBUG_MODE else "C:\\Presence\\Presence0.1\\Channels\\GodModeNotes\\Clips"

# Ancient effect overlay
ANCIENT_IMG = f"{ROOT_DIR}\\Resources\\Overlays\\ancient.jpg"

# Logo overlay
LOGO_PATH = f"{ROOT_DIR}\\Resources\\Avatar\\David-Goggins-no-background3.png"

# Font for Notepad
FONT_PATH = r"C:\\Windows\\Fonts\\consola.ttf"
FONT_SIZE = 48

# Video specs
WIDTH, HEIGHT = 1080, 1920
FPS = 60

# Make typing slower: about 70% speed => hold frames ~1 / 0.7 => ~1.4
# (i.e. if original hold was 5 frames, now it's ~7 frames)
SPEED_FACTOR = 4

def load_openai_key():
    try:
        with open(OPENAI_API_KEY_PATH, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: API key file not found!")
        return None

# -----------------------------------------------------------------
# 1) get_inspiration() from debug/offline/online
# -----------------------------------------------------------------
def get_inspiration():
    # DEBUG MODE
    if DEBUG_MODE:
        print("Getting inspiration - DEBUG mode")
        return DEBUG_TEXT, "debug"

    # OFFLINE MODE
    txt_files = glob.glob(os.path.join(DIR_OFFLINE_TEXT, "*.txt"))
    if txt_files:
        print("Getting inspiration - OFFLINE mode")
        txt_files.sort(key=lambda f: int(os.path.basename(f).split('.')[0]))
        selected_file = txt_files[0]
        with open(selected_file, 'r', encoding='utf-8') as file:
            text_content = file.read()
        shutil.move(selected_file, os.path.join(DIR_OFFLINE_TEXT_ARCHIVE, os.path.basename(selected_file)))
        print(f"Using text from file: {selected_file}")
        return text_content, "offline"

    # ONLINE MODE
    print("Getting inspiration - ONLINE mode")
    with open(PATH_PROMPT, 'r', encoding='utf-8') as file:
        prompt_content = file.read()

    print(f"✅ Final prompt sent to GPT API: {prompt_content}")

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o",  # or "gpt-3.5-turbo"
        "messages": [
            {"role": "system", "content": prompt_content}
        ]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    try:
        response_json = response.json()
        if "choices" not in response_json:
            return "No response from OpenAI", "online"
        text_response = response_json["choices"][0]["message"]["content"].strip()
        return text_response, "online"
    except Exception:
        return "Exception while getting response from OpenAI", "online"

# -----------------------------------------------------------------
# 2) AncientEffect Filters
# -----------------------------------------------------------------
def apply_soft_sepia(frame_bgr, intensity=0.07):
    sepia_filter = np.array([
        [0.272, 0.534, 0.131],
        [0.349, 0.686, 0.168],
        [0.393, 0.769, 0.189]
    ], dtype=np.float32)
    frame_float = frame_bgr.astype(np.float32)
    sepia_frame = cv2.transform(frame_float, sepia_filter)
    blended = cv2.addWeighted(frame_float, 1 - intensity, sepia_frame, intensity, 0)
    return np.clip(blended, 0, 255).astype(np.uint8)

def add_soft_vignette(frame_bgr, intensity=0.08):
    rows, cols = frame_bgr.shape[:2]
    X_kernel = cv2.getGaussianKernel(cols, cols * 0.8)
    Y_kernel = cv2.getGaussianKernel(rows, rows * 0.8)
    kernel = Y_kernel * X_kernel.T
    mask = 255 * kernel / np.linalg.norm(kernel)
    mask = mask.astype(np.float32) / 255.0

    frame_float = frame_bgr.astype(np.float32)
    vignette = np.zeros_like(frame_float, dtype=np.float32)
    for i in range(3):
        vignette[:, :, i] = (frame_float[:, :, i] * (1 - intensity)
                             + frame_float[:, :, i] * mask * intensity)

    return np.clip(vignette, 0, 255).astype(np.uint8)

def soft_flicker_effect(frame_bgr, intensity=0.03, flicker_rate=0.05):
    if random.random() < flicker_rate:
        factor = np.random.uniform(1 - intensity, 1 + intensity)
        frame_bgr = np.clip(frame_bgr.astype(np.float32) * factor, 0, 255).astype(np.uint8)
    return frame_bgr

def add_frame_jitter(frame_bgr, jitter_strength=0.5, jitter_rate=0.02):
    if random.random() < jitter_rate:
        rows, cols = frame_bgr.shape[:2]
        dx = np.random.randint(-jitter_strength, jitter_strength + 1)
        dy = np.random.randint(-jitter_strength, jitter_strength + 1)
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        frame_bgr = cv2.warpAffine(frame_bgr, M, (cols, rows))
    return frame_bgr

def overlay_image_on_video(frame_bgr, overlay_path, alpha=0.2):
    overlay = cv2.imread(overlay_path, cv2.IMREAD_COLOR)
    if overlay is None:
        return frame_bgr
    overlay = cv2.resize(overlay, (frame_bgr.shape[1], frame_bgr.shape[0]))
    return cv2.addWeighted(frame_bgr, 1 - alpha, overlay, alpha, 0)

def old_film_effect(frame_bgr):
    frame_bgr = apply_soft_sepia(frame_bgr, intensity=0.07)
    frame_bgr = add_soft_vignette(frame_bgr, intensity=0.08)
    frame_bgr = soft_flicker_effect(frame_bgr, intensity=0.03, flicker_rate=0.05)
    frame_bgr = add_frame_jitter(frame_bgr, jitter_strength=0.5, jitter_rate=0.02)
    if os.path.exists(ANCIENT_IMG):
        frame_bgr = overlay_image_on_video(frame_bgr, ANCIENT_IMG, alpha=0.2)
    return frame_bgr

# -----------------------------------------------------------------
# 3) Logo Overlay (bottom-right)
# -----------------------------------------------------------------
def overlay_logo_bottom_right(frame_bgr, logo_bgra, scale=1.0):
    if logo_bgra is None:
        return frame_bgr

    frame_h, frame_w = frame_bgr.shape[:2]
    logo_h = int(logo_bgra.shape[0] * scale)
    logo_w = int(logo_bgra.shape[1] * scale)

    if logo_h > frame_h or logo_w > frame_w:
        return frame_bgr

    logo_resized = cv2.resize(logo_bgra, (logo_w, logo_h), interpolation=cv2.INTER_AREA)

    if logo_resized.shape[2] == 4:
        bgr_logo = logo_resized[:, :, :3].astype(np.float32)
        alpha_ch = logo_resized[:, :, 3].astype(np.float32) / 255.0
    else:
        bgr_logo = logo_resized.astype(np.float32)
        alpha_ch = np.ones((logo_h, logo_w), dtype=np.float32)

    x_start = frame_w - logo_w - 10
    y_start = frame_h - logo_h - 10

    roi = frame_bgr[y_start:y_start+logo_h, x_start:x_start+logo_w].astype(np.float32)
    for c in range(3):
        roi[:, :, c] = roi[:, :, c] * (1 - alpha_ch) + bgr_logo[:, :, c] * alpha_ch

    frame_bgr[y_start:y_start+logo_h, x_start:x_start+logo_w] = np.clip(roi, 0, 255).astype(np.uint8)
    return frame_bgr

# -----------------------------------------------------------------
# 4) Word-Wrap (no word splits)
# -----------------------------------------------------------------
def wrap_text_by_words(text, max_chars=30):
    lines = []
    paragraphs = text.split('\n')
    for paragraph in paragraphs:
        words = paragraph.split()
        current_line = ""
        for w in words:
            if not current_line:
                current_line = w
            elif len(current_line) + 1 + len(w) <= max_chars:
                current_line += " " + w
            else:
                lines.append(current_line)
                current_line = w
        if current_line:
            lines.append(current_line)
        lines.append("")  # blank line to represent the forced newline
    if lines and lines[-1] == "":
        lines.pop()
    return lines

# -----------------------------------------------------------------
# 5) Typing Speed & Frame Calculation
# -----------------------------------------------------------------
def char_hold_frames(char, next_char):
    """
    Original hold frames logic, but scaled by SPEED_FACTOR for slower typing.
    """
    base_frames = random.randint(1, 2)
    if char in ",.!?":
        hold = base_frames + random.randint(2, 4)
    elif char == "\n" and next_char and next_char != "\n":
        hold = base_frames + random.randint(8, 12)
    elif char == "\n":
        hold = 1
    elif char.isspace():
        hold = base_frames + random.randint(1, 2)
    else:
        hold = base_frames

    # Increase hold by ~1.4 => slower typing
    scaled = max(1, int(hold * SPEED_FACTOR))
    return scaled

# -----------------------------------------------------------------
# 6) Render Frame
# -----------------------------------------------------------------
def render_frame(typed_text, font, brand_logo, frame_count, cursor_blink_rate):
    """
    Creates a single frame (PIL -> BGR) with typed_text + blinking cursor,
    then applies AncientEffect + logo overlay.
    """
    img_pil = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img_pil)

    y_offset = 200
    for line in typed_text.split("\n"):
        draw.text((100, y_offset), line, font=font, fill=(0, 0, 0))
        y_offset += font.size + 20

    # Blinking cursor
    if frame_count % cursor_blink_rate < (cursor_blink_rate // 2):
        last_line = typed_text.split("\n")[-1]
        text_width = font.getbbox(last_line)[2] if last_line else 0
        draw.text((100 + text_width, y_offset - (font.size + 20)),
                  "|", font=font, fill=(0, 0, 0))

    frame_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    frame_bgr = old_film_effect(frame_bgr)
    frame_bgr = overlay_logo_bottom_right(frame_bgr, brand_logo, scale=1.0)
    return frame_bgr

# -----------------------------------------------------------------
# 7) Extract Offline Title
# -----------------------------------------------------------------
def extract_offline_title(text):
    """
    In offline mode, returns a title that ends at the first punctuation
    (, . ! ? : ;) within the first 10 words, or if none found, the first
    10 words followed by '...' if there's more.
    """
    # Split into words
    words = text.strip().split()
    if not words:
        return ""  # empty text fallback

    # We'll only look at the first 10 words max
    snippet_words = words[:10]
    # Join them so we can find punctuation in the substring
    snippet_str = " ".join(snippet_words)

    # Allowed punctuation
    punctuations = [",", ".", "!", "?", ":", ";"]

    # Find the earliest punctuation index within snippet_str
    min_index = None
    for p in punctuations:
        idx = snippet_str.find(p)
        if idx != -1:
            if min_index is None or idx < min_index:
                min_index = idx

    # If we found punctuation within snippet_str
    if min_index is not None:
        # cut up to that punctuation
        return snippet_str[: min_index].strip()
    else:
        # No punctuation found in the first 10 words
        # If we have more than 10 words total => add "..."
        if len(words) > 10:
            return snippet_str + "..."
        else:
            return snippet_str  # 10 or fewer words, no punctuation

# -----------------------------------------------------------------
# 8) Main Orchestration
# -----------------------------------------------------------------
def main():
    OPENAI_API_KEY = load_openai_key()
    if OPENAI_API_KEY:
        print("API key loaded successfully.")

    # 1) Get text + mode
    text_content, mode = get_inspiration()

    # 2) Prepare title/desc for metadata
    if mode == "debug":
        title = "test"
        description = "test"
    elif mode == "offline":
        title = extract_offline_title(text_content)
        description = text_content
    else:  # "online"
        title = None
        for line in text_content.split('\n'):
            if line.lower().startswith("title:"):
                title = line.split(":", 1)[1].strip()
                break
        if not title:
            title = "ChatGPT Title"
        description = text_content

    # 3) Timestamped folder in OUT_BASE_FOLDER
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_folder = os.path.join(OUT_BASE_FOLDER, timestamp_str)
    os.makedirs(out_folder, exist_ok=True)

    # 4) Define paths
    video_silent_path = os.path.join(out_folder, f"{timestamp_str}_tmp_silent.mp4")
    final_video_path = os.path.join(out_folder, f"{timestamp_str}.mp4")
    metadata_path = os.path.join(out_folder, f"{timestamp_str}.json")

    # 5) Create metadata dict
    meta = {
        "title": title,
        "description": description,
        "creation_timestamp": timestamp_str,
        "mode": mode
    }

    # 6) Setup for writing silent video with OpenCV
    random.seed(42)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_silent_path, fourcc, FPS, (WIDTH, HEIGHT))

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    brand_logo = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)

    lines_wrapped = wrap_text_by_words(text_content, max_chars=30)

    typed_text = ""
    frame_count = 0
    cursor_blink_rate = 6

    # We'll track the times (in seconds) when each keystroke occurs
    keystroke_times = []

    # Type line by line, char by char
    for idx, line in enumerate(lines_wrapped):
        if line.strip() == "":
            # It's a forced newline
            typed_text += "\n"
            # Render just 1 char
            c = "\n"
            hold = char_hold_frames(c, None)
            for _ in range(hold):
                frame_bgr = render_frame(typed_text, font, brand_logo, frame_count, cursor_blink_rate)
                out.write(frame_bgr)
                # Log keystroke event => beginning of these frames
                if INCLUDE_TYPING_SOUNDS:
                    keystroke_times.append(frame_count / FPS)
                frame_count += 1
            continue

        # Else type out each char
        for i, char in enumerate(line):
            next_char = line[i+1] if i+1 < len(line) else None
            hold = char_hold_frames(char, next_char)
            typed_text += char
            for _ in range(hold):
                frame_bgr = render_frame(typed_text, font, brand_logo, frame_count, cursor_blink_rate)
                out.write(frame_bgr)
                # Mark the first frame of the typed char as the key time
                if _ == 0 and INCLUDE_TYPING_SOUNDS:
                    keystroke_times.append(frame_count / FPS)
                frame_count += 1

        # End of line => add newline
        typed_text += "\n"
        c = "\n"
        hold = char_hold_frames(c, None)
        for _ in range(hold):
            frame_bgr = render_frame(typed_text, font, brand_logo, frame_count, cursor_blink_rate)
            out.write(frame_bgr)
            if _ == 0 and INCLUDE_TYPING_SOUNDS:
                keystroke_times.append(frame_count / FPS)
            frame_count += 1

    # Hold final screen for 1 second
    last_frames = FPS
    for _ in range(last_frames):
        out.write(frame_bgr)
        frame_count += 1

    out.release()

    # 7) Merge Audio: background + typing sounds => final mp4
    # --------------------------------------------------------
    video_duration = frame_count / FPS

    # (a) Load final silent video
    video_clip = VideoFileClip(video_silent_path)

    # (b) Build background audio track
    if os.path.exists(BACKGROUND_AUDIO):
        bg_audio_clip = AudioFileClip(BACKGROUND_AUDIO).subclipped(0, video_duration)
    else:
        bg_audio_clip = None

    # (c) Build typing sounds as multiple short audio clips
    keystroke_audio_clips = []
    if INCLUDE_TYPING_SOUNDS:
        # Gather typing sound files
        typing_sounds = []
        if os.path.isdir(TYPING_SOUNDS_DIR):
            typing_sounds = [
                os.path.join(TYPING_SOUNDS_DIR, f)
                for f in os.listdir(TYPING_SOUNDS_DIR)
                if f.lower().endswith(('.wav', '.mp3'))
            ]

        if typing_sounds:
            for t in keystroke_times:
                snd_file = random.choice(typing_sounds)
                # Start this clip at time t
                snd_clip = AudioFileClip(snd_file).with_start(t)
                keystroke_audio_clips.append(snd_clip)

    # (d) Composite all audio layers
    if bg_audio_clip and keystroke_audio_clips:
        final_audio = CompositeAudioClip([bg_audio_clip] + keystroke_audio_clips)
    elif bg_audio_clip:
        final_audio = bg_audio_clip
    elif keystroke_audio_clips:
        final_audio = CompositeAudioClip(keystroke_audio_clips)
    else:
        final_audio = None

    # (e) Attach audio to video clip
    if final_audio:
        video_with_audio = video_clip.with_audio(final_audio)
    else:
        video_with_audio = video_clip  # no audio at all

    # (f) Write final MP4
    video_with_audio.write_videofile(final_video_path, codec="libx264", fps=FPS, audio_codec="aac")

    # (g) Remove temp silent file
    if os.path.exists(video_silent_path):
        os.remove(video_silent_path)

    # 8) Save metadata.json
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)

    print(f"✅ Done! Final video: {final_video_path}")
    print(f"   Metadata JSON: {metadata_path}")


if __name__ == "__main__":
    main()
