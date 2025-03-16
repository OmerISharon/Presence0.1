#!/usr/bin/env python3

import os
import cv2
import numpy as np
import random
import json
import re
import requests
from datetime import datetime
from moviepy import (ImageClip, VideoClip, concatenate_videoclips, 
                     AudioFileClip, CompositeAudioClip)
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
from PIL import Image, ImageDraw, ImageFont
from TTS.api import TTS             # Coqui TTS
from config import *
from pydub import AudioSegment      # For audio processing (echo effect)

def load_openai_key():
    try:
        with open(OPENAI_API_KEY_PATH, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: API key file not found!")
        return None

def get_clip_title_using_chatgpt(quote):
    """
    Use the ChatGPT API via requests to generate a simple, short, and clear title for the quote.
    Ensure that the OPENAI_API_KEY environment variable is set.
    """
    openai_api_key = load_openai_key()
    if not openai_api_key:
        print("OPENAI_API_KEY not set. Falling back to local title extraction.")
        quit()
        return get_title_from_quote(quote)
    
    print(f"OPENAI_API_KEY found: {openai_api_key}")
    
    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    prompt = f"Generate a simple, short, and clear title for the following quote (dont use quotes):\n\n\"{quote}\""
    data = {
        "model": GPT_MODULE,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 10
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        title = result["choices"][0]["message"]["content"].strip()
        return title
    except Exception as e:
        print(f"Error calling ChatGPT API: {e}")
        return get_title_from_quote(quote)

def get_keywords_from_gpt(quote):
    """
    If USE_KEYWORDS_BOLT_EFFECT is True, this function sends a request to ChatGPT to extract up to 5
    inspiring, positive, standalone keywords that appear verbatim in the quote.
    Return only a comma-separated list of words with no extra text.
    """
    openai_api_key = load_openai_key()
    if not openai_api_key:
        print("OPENAI_API_KEY not set. Cannot retrieve keywords.")
        return []
    
    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    prompt = (
        f"Given the following quote, extract up to 5 keywords that are extremely positive, uplifting, and inspiring. "
        f"Only include words that are unequivocally positive and motivational—do not include any negative, ambiguous, or neutral words. "
        f"Return only the best, most impactful, standalone keywords exactly as they appear in the quote, separated by commas, with no additional text or explanation.\n\n\"{quote}\""
    )
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 30
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        keywords_str = result["choices"][0]["message"]["content"].strip()
        keywords = [kw.strip().lower() for kw in keywords_str.split(",") if kw.strip()]
        return keywords[:5] if keywords else []
    except Exception as e:
        print(f"Error retrieving keywords: {e}")
        return []

# ---------------------------
# New TTS Function using Coqui TTS (with echo effect)
# ---------------------------
import soundfile as sf

def generate_tts_audio(text, output_path, model=MODEL_NAME, speaker=SPEAKER_TYPE, 
                       echo_intensity=TTS_ECHO_INTENSITY, slowdown_factor=TTS_SPEED, volume=TTS_VOLUME):
    """
    Generate TTS audio from text using Coqui TTS with a wise-sounding voice.
    Then apply an echo effect, slow down the audio, and lower its volume.
    Finally, export a single MP3 file (final with echo, slowdown, and reduced volume).

    Parameters:
      text           : The text to synthesize.
      output_path    : Path to save the final MP3 audio file.
      model          : TTS model name.
      speaker        : Speaker ID for the TTS model.
      echo_intensity : Float (0 to 1) controlling the echo intensity.
      slowdown_factor: Factor to slow down the audio (e.g. 0.9 slows it by 10%).
      volume         : Volume adjustment in dB.
    """
    # Generate raw TTS audio (as a numpy waveform) with a slower speaking rate using length_scale
    temp_path = output_path.replace(".mp3", "_temp.wav")
    tts = TTS(model_name=model, progress_bar=False, gpu=False)
    # Generate waveform with length_scale set to 1.5 (adjust as desired)
    wav = tts.tts(text, length_scale=5, speaker=speaker)
    
    # Attempt to obtain sample rate from the synthesizer config, fallback to 22050 Hz if unavailable.
    try:
        sample_rate = tts.synthesizer.config.audio["sample_rate"]
    except Exception:
        sample_rate = 22050

    # Save waveform to temporary WAV file using the determined sample rate
    sf.write(temp_path, wav, samplerate=sample_rate)
    
    # Load the generated audio using pydub
    audio = AudioSegment.from_file(temp_path)
    
    # Apply echo effect
    delay_ms = 100  # echo delay in milliseconds
    attenuation_db = 20 * (1 - echo_intensity)
    echo = audio - attenuation_db
    audio_with_echo = audio.overlay(echo, position=delay_ms)
    
    # Slow down the audio using pydub (by adjusting the frame rate)
    slowed_audio = audio_with_echo._spawn(
        audio_with_echo.raw_data,
        overrides={"frame_rate": int(audio_with_echo.frame_rate * slowdown_factor)}
    ).set_frame_rate(audio_with_echo.frame_rate)
    
    # Adjust volume according to the provided volume (in dB)
    adjusted_audio = slowed_audio.apply_gain(volume)
    
    # Export the final processed audio as a single MP3 file
    adjusted_audio.export(output_path, format="mp3")
    
    # Remove the temporary WAV file
    os.remove(temp_path)

# ---------------------------
# New Functionality: Random Quote Selection and Update
# ---------------------------
def get_random_quote_and_update_json(json_path):
    """Load quotes from a JSON file, choose a random quote with GPT Score >= 70
    that has the lowest 'Number Usage' among such quotes,
    increment its 'Number Usage' by 1 (unless in debug mode),
    update the file, and return the entire quote dictionary."""
    with open(json_path, "r") as f:
        quotes = json.load(f)
    filtered_quotes = [q for q in quotes if q.get("GPT Score", 0) >= 70]
    if not filtered_quotes:
        raise ValueError("No quotes with GPT Score >= 70 found.")
    min_usage = min(q.get("Number Usage", 0) for q in filtered_quotes)
    least_used_quotes = [q for q in filtered_quotes if q.get("Number Usage", 0) == min_usage]
    chosen_quote = random.choice(least_used_quotes)
    if not DEBUG_MODE:
        chosen_quote["Number Usage"] += 1
        with open(json_path, "w") as f:
            json.dump(quotes, f, indent=4)
    return chosen_quote

# ---------------------------
# Updated TEXT - now chosen dynamically from the JSON file
# ---------------------------
chosen_quote = get_random_quote_and_update_json(QUOTE_JSON_PATH)
TEXT_TO_TYPE = chosen_quote["Quote"].replace(";", ".")

# ---------------------------
# Utility Function: Get title from quote and sanitize it for folder names
# ---------------------------
def get_title_from_quote(quote):
    """
    Return a title extracted from the quote as the first up to 5 words.
    We only stop early if a word starts with a special character.
    """
    words = quote.split()
    title_words = []
    for word in words:
        if word and word[0] in SPECIAL_CHARS:
            break
        title_words.append(word)
        if len(title_words) == 5:
            break
    if title_words:
        return " ".join(title_words)
    return quote.strip()

def sanitize_filename(name):
    """Sanitize a string to be safe for use as a folder or file name."""
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

# ---------------------------
# Utility Functions
# ---------------------------
def load_and_resize_image(path, width, height):
    """Load an image from disk and resize (stretch) it to the given dimensions."""
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image from {path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    return img

def create_blank_page_composite(blank_img):
    """Composite the blank image at 50% alpha over a full white background."""
    white_bg = np.full_like(blank_img, 255)
    composite = cv2.addWeighted(blank_img, 0.5, white_bg, 0.5, 0)
    return composite

def wrap_text_to_lines(text, font, max_width):
    """Wrap text so that each line's pixel width does not exceed max_width, preserving explicit newlines."""
    lines = []
    # First split by explicit newline
    for raw_line in text.split("\n"):
        words = raw_line.split()
        if not words:
            lines.append("")
            continue
        current_line = words[0]
        for word in words[1:]:
            test_line = current_line + " " + word
            bbox = font.getbbox(test_line)
            width_text = bbox[2] - bbox[0]
            if width_text <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
    return lines

# New helper: Draw progressive text based on final token segmentation.
def draw_progressive_text(background, tokens, num_chars, font, position, max_width, line_spacing=30):
    opacity = int(0.85 * 255)
    default_color = TEXT_COLOR + (opacity,) if isinstance(TEXT_COLOR, tuple) and len(TEXT_COLOR) == 3 else (0, 0, 0, opacity)
    image_pil = Image.fromarray(background).convert("RGBA")
    txt_overlay = Image.new("RGBA", image_pil.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_overlay)
    x, y = position
    cumulative = 0
    for token, is_keyword in tokens:
        if token == "\n":
            bbox_line = font.getbbox("Ay")
            line_height = bbox_line[3] - bbox_line[1]
            y += line_height + line_spacing
            x = position[0]
            cumulative += len(token)
            continue
        if cumulative >= num_chars:
            reveal_text = ""
        elif cumulative + len(token) <= num_chars:
            reveal_text = token
        else:
            reveal_text = token[:num_chars - cumulative]
        if reveal_text:
            token_width = font.getbbox(reveal_text)[2] - font.getbbox(reveal_text)[0]
            shadow_offset = (2, 2)
            shadow_color = (0, 0, 0, int(opacity * 0.7))
            if is_keyword:
                token_color = KEYWORD_COLOR + (opacity,)
                draw.text((x + shadow_offset[0], y + shadow_offset[1]), reveal_text, font=font, fill=shadow_color)
                draw.text((x, y), reveal_text, font=font, fill=token_color)
                draw.text((x + 1, y), reveal_text, font=font, fill=token_color)
            else:
                draw.text((x + shadow_offset[0], y + shadow_offset[1]), reveal_text, font=font, fill=shadow_color)
                draw.text((x, y), reveal_text, font=font, fill=default_color)
            x += token_width
        cumulative += len(token)
    combined = Image.alpha_composite(image_pil, txt_overlay)
    return np.array(combined.convert("RGB"))

# ---------------------------
# Drawing function that uses the standard approach when no keywords are provided.
def draw_text_on_image(background, text, font, position, max_width, line_spacing=30, keywords=None):
    """
    Draw text on the given background.
    This function is used when no progressive token segmentation is needed.
    """
    opacity = int(0.85 * 255)
    image_pil = Image.fromarray(background).convert("RGBA")
    txt_overlay = Image.new("RGBA", image_pil.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_overlay)
    lines = []
    for part in text.split("\n"):
        wrapped = wrap_text_to_lines(part, font, max_width)
        lines.extend(wrapped)
    x, y = position
    default_color = TEXT_COLOR + (opacity,) if isinstance(TEXT_COLOR, tuple) and len(TEXT_COLOR) == 3 else (0, 0, 0, opacity)
    keywords_set = set(kw.lower() for kw in keywords) if keywords else set()
    for line in lines:
        current_x = x
        tokens = re.split(r'(\s+)', line)
        for token in tokens:
            bbox = font.getbbox(token)
            token_width = bbox[2] - bbox[0]
            cleaned = re.sub(r'[^\w]', '', token).lower()
            if cleaned in keywords_set and token.strip() == cleaned:
                token_color = KEYWORD_COLOR + (opacity,)
                shadow_offset = (2, 2)
                shadow_color = (0, 0, 0, int(opacity * 0.7))
                draw.text((current_x + shadow_offset[0], y + shadow_offset[1]), token, font=font, fill=shadow_color)
                draw.text((current_x, y), token, font=font, fill=token_color)
                draw.text((current_x + 1, y), token, font=font, fill=token_color)
            else:
                shadow_offset = (2, 2)
                shadow_color = (0, 0, 0, int(opacity * 0.7))
                draw.text((current_x + shadow_offset[0], y + shadow_offset[1]), token, font=font, fill=shadow_color)
                draw.text((current_x, y), token, font=font, fill=default_color)
            current_x += token_width
        bbox_line = font.getbbox(line)
        line_height = bbox_line[3] - bbox_line[1]
        y += line_height + line_spacing
    combined = Image.alpha_composite(image_pil, txt_overlay)
    return np.array(combined.convert("RGB"))

# ---------------------------
# Additional Effects for an Ancient Feel (Lighter Version)
# ---------------------------
def apply_vignette(frame, strength=0.8):
    """Apply a vignette effect to the frame using a Gaussian kernel with a lighter strength."""
    rows, cols = frame.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols * strength)
    kernel_y = cv2.getGaussianKernel(rows, rows * strength)
    kernel = kernel_y * kernel_x.T
    mask = kernel / kernel.max()
    vignette = np.copy(frame)
    for i in range(3):
        vignette[:, :, i] = vignette[:, :, i] * mask
    vignette = np.clip(vignette, 0, 255).astype(np.uint8)
    return vignette

# New: Color Grading for a Cinematic Look
def apply_color_grade(frame, alpha=1.1, beta=10):
    """Apply a cinematic color grade by adjusting contrast (alpha) and brightness (beta)."""
    graded = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
    return graded

# ---------------------------
# Enhanced Ancient Effect (Lighter Version)
# ---------------------------
ancient_effect_cache = {}

def apply_ancient_effect(frame):
    """
    Apply a lighter ancient film effect including subtle grain, sepia tone, and a light vignette.
    Uses caching to avoid recomputation for identical frames.
    """
    frame_bytes = frame.tobytes()
    frame_shape = frame.shape
    cache_key = (frame_bytes, frame_shape)
    if cache_key in ancient_effect_cache:
        return ancient_effect_cache[cache_key]
    
    noise = np.random.randn(*frame.shape) * 3
    frame_noisy = frame.astype(np.float32) + noise
    frame_noisy = np.clip(frame_noisy, 0, 255).astype(np.uint8)
    
    sepia_filter = np.array([[0.95, 0.05, 0],
                             [0.05, 0.95, 0],
                             [0,    0,    0.95]])
    frame_sepia = frame_noisy.astype(np.float32)
    frame_sepia = frame_sepia @ sepia_filter.T
    frame_sepia = np.clip(frame_sepia, 0, 255).astype(np.uint8)
    
    frame_vignette = apply_vignette(frame_sepia, strength=0.8)
    
    ancient_effect_cache[cache_key] = frame_vignette
    if len(ancient_effect_cache) > 1000:
        ancient_effect_cache.pop(next(iter(ancient_effect_cache)))
    
    return frame_vignette

def compute_typing_schedule(text, cps, font, max_width, delay_line=DELAY_LINE_BREAK, delay_special=DELAY_SPECIAL_CHAR):
    """Compute a schedule (cumulative times) for each character in text based on cps and extra delays."""
    schedule = []
    current_time = 0.0
    base_delay = 1.0 / cps
    for ch in text:
        if ch == "\n":
            current_time += delay_line
            schedule.append(current_time)
            continue
        extra = delay_special if ch in SPECIAL_CHARS else 0.0
        current_time += base_delay + extra
        schedule.append(current_time)
    return schedule

# ---------------------------
# Clip Generators (Optimized)
# ---------------------------
def make_static_clip(image, duration):
    """Return an ImageClip from a numpy image with the given duration."""
    return ImageClip(image).with_duration(duration).with_fps(FPS)

def make_transition_clip(img_start, img_end, duration):
    """
    Create a video clip that crossfades from img_start to img_end over duration,
    with a dynamic zoom effect for enhanced visual appeal.
    """
    num_frames = int(duration * FPS)
    transition_frames = []
    
    def zoom_image(img, factor):
        h, w = img.shape[:2]
        new_w = int(w * factor)
        new_h = int(h * factor)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        start_x = (new_w - w) // 2
        start_y = (new_h - h) // 2
        return resized[start_y:start_y+h, start_x:start_x+w]
    
    for i in range(num_frames):
        progress = i / num_frames
        zoom_factor = 1 + 0.05 * progress
        zoomed_start = zoom_image(img_start, zoom_factor)
        zoomed_end = zoom_image(img_end, zoom_factor)
        frame = cv2.addWeighted(zoomed_start, 1 - progress, zoomed_end, progress, 0)
        transition_frames.append(frame)
    
    def make_frame(t):
        frame_idx = min(int(t * FPS), num_frames - 1)
        return transition_frames[frame_idx]
        
    return VideoClip(make_frame, duration=duration).with_fps(FPS)

def make_typing_clip(background, text, cps, font, position=(LEFT_MARGIN, TEXT_TOP), delay_line=DELAY_LINE_BREAK, keywords=None):
    max_text_width = VIDEO_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    stable_lines = wrap_text_to_lines(text, font, max_text_width)
    stable_text = "\n".join(stable_lines)
    schedule = compute_typing_schedule(stable_text, cps, font, max_text_width, delay_line=0.001)
    duration = schedule[-1]
    
    # Precompute token segmentation of the final stable text.
    if keywords:
        keywords_set = set(kw.lower() for kw in keywords)
    else:
        keywords_set = set()
    raw_tokens = re.split(r'(\s+)', stable_text)
    tokens = []
    for token in raw_tokens:
        if token.isspace():
            tokens.append((token, False))
        else:
            cleaned = re.sub(r'[^\w]', '', token).lower()
            is_kw = (cleaned in keywords_set) if keywords_set else False
            tokens.append((token, is_kw))
    
    num_frames = int(duration * FPS) + 1
    time_list = np.linspace(0, duration, num_frames).tolist()
    
    frame_list = []
    for t in time_list:
        num_chars = sum(1 for sched in schedule if sched <= t)
        if num_chars > len(stable_text):
            num_chars = len(stable_text)
        # Draw using the progressive token approach.
        current_frame = background.copy()
        frame_with_text = draw_progressive_text(current_frame, tokens, num_chars, font, position, max_text_width, line_spacing=30)
        frame_list.append(frame_with_text)
    
    def make_frame(t):
        index = min(int(round(t * FPS)), len(frame_list) - 1)
        return frame_list[index]
    
    return VideoClip(make_frame, duration=duration).with_fps(FPS)

# ---------------------------
# Main Script
# ---------------------------
def main():
    if DEBUG_MODE:
        title = get_title_from_quote(TEXT_TO_TYPE)
    else:
        title = get_clip_title_using_chatgpt(TEXT_TO_TYPE)
    sanitized_title = sanitize_filename(title)
    
    if USE_KEYWORDS_BOLT_EFFECT:
        keywords = get_keywords_from_gpt(TEXT_TO_TYPE)
        print("Quote:", chosen_quote)
        print("Extracted keywords:", keywords)
    else:
        keywords = None

    if DEBUG_MODE:
        output_folder = os.path.join(DEBUG_MODE_OUTPUT_DIR, sanitized_title)
    else:
        output_folder = os.path.join(OUT_BASE_FOLDER, sanitized_title)
    os.makedirs(output_folder, exist_ok=True)
    
    output_video_path = os.path.join(output_folder, f"{sanitized_title}.mp4")
    metadata_json_path = os.path.join(output_folder, "metadata.json")
    temp_audio_path = os.path.join(output_folder, "temp_audio.m4a")
    
    book_cover = load_and_resize_image(IMG_BOOK_COVER_PATH, VIDEO_WIDTH, VIDEO_HEIGHT)
    blank_page_raw = load_and_resize_image(IMG_BLANK_PAGE_PATH, VIDEO_WIDTH, VIDEO_HEIGHT)
    blank_page = create_blank_page_composite(blank_page_raw)
    
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()
    try:
        font_author = ImageFont.truetype(FONT_PATH_AUTHOR, FONT_SIZE_AUTHOR)
    except Exception:
        font_author = ImageFont.load_default()
    
    print("Pre-computing frames to optimize rendering...")
    
    clip1 = make_static_clip(book_cover, DURATION_BOOK_COVER)
    transition_clip = make_transition_clip(book_cover, blank_page, DURATION_TRANSITION)
    clip3 = make_static_clip(blank_page, DURATION_BLANK_FREEZE)
    
    print("Generating typing clip frames...")
    typing_clip = make_typing_clip(blank_page, TEXT_TO_TYPE, TYPING_CPS, font, keywords=keywords)
    
    final_text_frame = typing_clip.get_frame(typing_clip.duration)
    
    quote_freeze_clip = make_static_clip(final_text_frame, 3)
    
    print("Generating author typing clip frames...")
    author_text = f"{chosen_quote['Author']}\n{chosen_quote['Book Title']}"
    author_position = (LEFT_MARGIN, VIDEO_HEIGHT - FONT_SIZE_AUTHOR - 180)
    author_typing_clip = make_typing_clip(final_text_frame, author_text, TYPING_CPS, font_author, position=author_position, delay_line=0.001)
    
    final_complete_frame = author_typing_clip.get_frame(author_typing_clip.duration)
    
    final_freeze_clip = make_static_clip(final_complete_frame, 5)
    
    print("Concatenating video segments...")
    final_clip = concatenate_videoclips([
        clip1,
        transition_clip,
        clip3,
        typing_clip,
        quote_freeze_clip,
        author_typing_clip,
        final_freeze_clip
    ])
    
    print("Applying ancient effect with optimization...")
    apply_ancient_effect(book_cover)
    apply_ancient_effect(blank_page)
    apply_ancient_effect(final_text_frame)
    apply_ancient_effect(final_complete_frame)
    
    def final_make_frame(t):
        frame = final_clip.get_frame(t)
        processed_frame = apply_ancient_effect(frame)
        processed_frame = apply_color_grade(processed_frame)
        flicker = random.uniform(0.99, 1.01)
        processed_frame = np.clip(processed_frame * flicker, 0, 255).astype(np.uint8)
        return processed_frame
    
    final_clip_processed = VideoClip(final_make_frame, duration=final_clip.duration).with_fps(FPS)
    
    print("Adding sound effects, background music, and TTS narration...")
    T_typing_start = DURATION_BOOK_COVER + DURATION_TRANSITION + DURATION_BLANK_FREEZE
    typing_sound_clips = []
    max_text_width = VIDEO_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    
    char_sound_files = [os.path.join(TYPING_SOUNDS_DIR, f) for f in os.listdir(TYPING_SOUNDS_DIR)
                        if f.startswith("Char") and f.lower().endswith('.mp3')]
    space_sound_files = [os.path.join(TYPING_SOUNDS_DIR, f) for f in os.listdir(TYPING_SOUNDS_DIR)
                         if f.startswith("Space") and f.lower().endswith('.mp3')]
    enter_sound_files = [os.path.join(TYPING_SOUNDS_DIR, f) for f in os.listdir(TYPING_SOUNDS_DIR)
                         if f.startswith("Enter") and f.lower().endswith('.mp3')]
    
    stable_lines = wrap_text_to_lines(TEXT_TO_TYPE, font, max_text_width)
    stable_text = "\n".join(stable_lines)
    typing_schedule = compute_typing_schedule(stable_text, TYPING_CPS, font, max_text_width, delay_line=0.001)
    
    # Shift audio slightly earlier to improve perceived sync
    normal_char_count = 0
    SHIFT_OFFSET = 0.02
    for i, ch in enumerate(stable_text):
        t_start = T_typing_start + typing_schedule[i] - SHIFT_OFFSET
        if t_start < 0:
            t_start = 0
        if ch == "\n":
            if enter_sound_files:
                sound_file = random.choice(enter_sound_files)
                try:
                    sound_clip = AudioFileClip(sound_file).with_start(t_start)
                    typing_sound_clips.append(sound_clip)
                except Exception as e:
                    print(f"Error loading sound {sound_file}: {e}")
        elif ch == " ":
            if space_sound_files:
                sound_file = random.choice(space_sound_files)
                try:
                    sound_clip = AudioFileClip(sound_file).with_start(t_start)
                    typing_sound_clips.append(sound_clip)
                except Exception as e:
                    print(f"Error loading sound {sound_file}: {e}")
        else:
            normal_char_count += 1
            if normal_char_count % 2 == 0:
                if char_sound_files:
                    sound_file = random.choice(char_sound_files)
                    try:
                        sound_clip = AudioFileClip(sound_file).with_start(t_start)
                        typing_sound_clips.append(sound_clip)
                    except Exception as e:
                        print(f"Error loading sound {sound_file}: {e}")
    
    author_typing_start = T_typing_start + typing_clip.duration + 3
    stable_author_lines = wrap_text_to_lines(author_text, font_author, max_text_width)
    stable_author_text = "\n".join(stable_author_lines)
    author_schedule = compute_typing_schedule(stable_author_text, TYPING_CPS, font_author, max_text_width, delay_line=0.001)
    
    # Also shift audio slightly earlier for author typing
    normal_char_count_author = 0
    SHIFT_OFFSET_AUTHOR = 0.02
    for i, ch in enumerate(stable_author_text):
        t_start = author_typing_start + author_schedule[i] - SHIFT_OFFSET_AUTHOR
        if t_start < 0:
            t_start = 0
        if ch == "\n":
            if enter_sound_files:
                sound_file = random.choice(enter_sound_files)
                try:
                    sound_clip = AudioFileClip(sound_file).with_start(t_start)
                    typing_sound_clips.append(sound_clip)
                except Exception as e:
                    print(f"Error loading sound {sound_file}: {e}")
        elif ch == " ":
            if space_sound_files:
                sound_file = random.choice(space_sound_files)
                try:
                    sound_clip = AudioFileClip(sound_file).with_start(t_start)
                    typing_sound_clips.append(sound_clip)
                except Exception as e:
                    print(f"Error loading sound {sound_file}: {e}")
        else:
            normal_char_count_author += 1
            if normal_char_count_author % 2 == 0:
                if char_sound_files:
                    sound_file = random.choice(char_sound_files)
                    try:
                        sound_clip = AudioFileClip(sound_file).with_start(t_start)
                        typing_sound_clips.append(sound_clip)
                    except Exception as e:
                        print(f"Error loading sound {sound_file}: {e}")
    
    # NEW: Generate final TTS narration audio (with echo and slowdown) as a single MP3 file.
    tts_audio_path = os.path.join(output_folder, "tts_audio.mp3")
    generate_tts_audio(TEXT_TO_TYPE, tts_audio_path, model=MODEL_NAME, speaker=SPEAKER_TYPE, echo_intensity=TTS_ECHO_INTENSITY, slowdown_factor=TTS_SPEED)
    try:
        tts_audio_clip = AudioFileClip(tts_audio_path).with_start(T_typing_start)
    except Exception as e:
        print(f"Error processing TTS audio: {e}")
        tts_audio_clip = None

    overlay_music = None
    if OVERLAY_MUSIC_PATH and os.path.exists(OVERLAY_MUSIC_PATH):
        try:
            bg_duration = OVERLAY_MUSIC_DURATION if OVERLAY_MUSIC_DURATION != 0 else final_clip_processed.duration
            overlay_music = AudioFileClip(OVERLAY_MUSIC_PATH).with_duration(bg_duration)
            overlay_music = overlay_music.with_start(OVERLAY_MUSIC_START_AT)
            fadeout_effect = AudioFadeOut(OVERLAY_FADEOUT_DURATION) 
            overlay_music = fadeout_effect.apply(overlay_music)
        except Exception as e:
            print(f"Error loading overlay music from {OVERLAY_MUSIC_PATH}: {e}")
    else:
        print(f"OVERLAY_MUSIC_PATH not found: {OVERLAY_MUSIC_PATH}")


    # Load permanent background music if specified.
    bg_music = None
    if BACKGROUND_MUSIC_PATH and os.path.exists(BACKGROUND_MUSIC_PATH):
        try:
            bg_music = AudioFileClip(BACKGROUND_MUSIC_PATH)
        except Exception as e:
            print(f"Error loading background music from {BACKGROUND_MUSIC_PATH}: {e}")

    # Build a list of audio clips to combine.
    audio_clips = []
    if tts_audio_clip:
        audio_clips.append(tts_audio_clip)
    if typing_sound_clips:
        typing_audio = CompositeAudioClip(typing_sound_clips).with_duration(final_clip_processed.duration)
        audio_clips.append(typing_audio)
    if overlay_music:
        audio_clips.append(overlay_music)
    if bg_music:
        audio_clips.append(bg_music)

    if audio_clips:
        composite_audio = CompositeAudioClip(audio_clips).with_duration(final_clip_processed.duration)
    else:
        composite_audio = None

    if composite_audio:
        # Now attach the combined composite audio to the final video.
        final_clip_processed = final_clip_processed.with_audio(composite_audio)

    
    print("Writing video file...")
    final_clip_processed.write_videofile(
        output_video_path,
        codec="libx264",
        fps=FPS,
        temp_audiofile=os.path.join(output_folder, "temp_audio.aac"),
        remove_temp=True,
        audio_codec="aac",
        threads=4,
        preset="faster",
        ffmpeg_params=["-tune", "fastdecode"]
    )
    
    metadata = {
        "title": title,
        "description": TEXT_TO_TYPE,
        "creation_timestamp": datetime.now().isoformat()
    }
    with open(metadata_json_path, "w") as meta_file:
        json.dump(metadata, meta_file, indent=4)
    
    print(f"Video generated successfully at: {output_video_path}")
    print(f"Metadata saved at: {metadata_json_path}")
    
    try:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"Temporary file {temp_audio_path} removed.")
    except Exception as e:
        print(f"Could not remove temporary file {temp_audio_path}: {e}")

if __name__ == "__main__":
    print("Starts Creator_TheScienceOfGettingRich.py")
    main()
