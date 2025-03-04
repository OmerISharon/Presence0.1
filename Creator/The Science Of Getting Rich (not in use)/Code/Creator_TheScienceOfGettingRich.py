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
from PIL import Image, ImageDraw, ImageFont
from config import *

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
    prompt = f"Generate a simple, short, and clear title for the following quote:\n\n\"{quote}\""
    data = {
        "model": "gpt-3.5-turbo",
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
    # Filter quotes to only include those with GPT Score of 70 or higher
    filtered_quotes = [q for q in quotes if q.get("GPT Score", 0) >= 70]
    if not filtered_quotes:
        raise ValueError("No quotes with GPT Score >= 70 found.")
    # Find the minimum Number Usage among filtered quotes
    min_usage = min(q.get("Number Usage", 0) for q in filtered_quotes)
    # Filter further: choose only those with Number Usage equal to min_usage
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
    """Wrap text so that each line's pixel width does not exceed max_width."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = font.getbbox(test_line)
        width_text = bbox[2] - bbox[0]
        if width_text <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def draw_text_on_image(background, text, font, position, max_width, line_spacing=20):
    opacity = int(0.85 * 255)

    image_pil = Image.fromarray(background).convert("RGBA")
    txt_overlay = Image.new("RGBA", image_pil.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_overlay)
    
    lines = []
    for part in text.split("\n"):
        wrapped = wrap_text_to_lines(part, font, max_width)
        lines.extend(wrapped)
    x, y = position
    fill_color = TEXT_COLOR + (opacity,) if isinstance(TEXT_COLOR, tuple) and len(TEXT_COLOR) == 3 else (0, 0, 0, opacity)
    
    for line in lines:
        # Draw drop shadow
        shadow_offset = (2, 2)
        shadow_color = (0, 0, 0, int(opacity * 0.7))
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), line, font=font, fill=shadow_color)
        # Draw main text on top
        draw.text((x, y), line, font=font, fill=fill_color)
        bbox = font.getbbox(line)
        line_height = bbox[3] - bbox[1]
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
    # Convert frame to a hashable type for caching
    frame_bytes = frame.tobytes()
    frame_shape = frame.shape
    cache_key = (frame_bytes, frame_shape)
    if cache_key in ancient_effect_cache:
        return ancient_effect_cache[cache_key]
    
    # Add lighter grain
    noise = np.random.randn(*frame.shape) * 3  # Reduced noise level
    frame_noisy = frame.astype(np.float32) + noise
    frame_noisy = np.clip(frame_noisy, 0, 255).astype(np.uint8)
    
    # Apply a sepia filter (unchanged)
    sepia_filter = np.array([[0.95, 0.05, 0],
                             [0.05, 0.95, 0],
                             [0,    0,    0.95]])
    frame_sepia = frame_noisy.astype(np.float32)
    frame_sepia = frame_sepia @ sepia_filter.T
    frame_sepia = np.clip(frame_sepia, 0, 255).astype(np.uint8)
    
    # Apply lighter vignette effect
    frame_vignette = apply_vignette(frame_sepia, strength=0.8)
    
    # Cache the result
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
        # Crop center to original size
        start_x = (new_w - w) // 2
        start_y = (new_h - h) // 2
        return resized[start_y:start_y+h, start_x:start_x+w]
    
    for i in range(num_frames):
        progress = i / num_frames
        zoom_factor = 1 + 0.05 * progress  # Zoom factor ramps from 1.0 to 1.05
        zoomed_start = zoom_image(img_start, zoom_factor)
        zoomed_end = zoom_image(img_end, zoom_factor)
        frame = cv2.addWeighted(zoomed_start, 1 - progress, zoomed_end, progress, 0)
        transition_frames.append(frame)
    
    def make_frame(t):
        frame_idx = min(int(t * FPS), num_frames - 1)
        return transition_frames[frame_idx]
        
    return VideoClip(make_frame, duration=duration).with_fps(FPS)

def make_typing_clip(background, text, cps, font, position=(LEFT_MARGIN, TEXT_TOP), delay_line=DELAY_LINE_BREAK):
    max_text_width = VIDEO_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    schedule = compute_typing_schedule(text, cps, font, max_text_width, delay_line=delay_line)
    duration = schedule[-1]
    
    # Generate timestamps using linspace to include both endpoints
    num_frames = int(duration * FPS) + 1
    time_list = np.linspace(0, duration, num_frames).tolist()
    
    frame_list = []
    for t in time_list:
        # If we're at (or extremely close to) the final timestamp, show full text.
        if abs(t - duration) < 1e-6:
            current_text = text
        else:
            num_chars = sum(1 for sched in schedule if sched <= t)
            # Ensure we don't exceed the text length.
            if num_chars > len(text):
                num_chars = len(text)
            current_text = text[:num_chars]
        frame = background.copy()
        frame_with_text = draw_text_on_image(frame, current_text, font, position, max_text_width)
        frame_list.append(frame_with_text)
    
    def make_frame(t):
        # Round t * FPS to get the proper frame index.
        index = min(int(round(t * FPS)), len(frame_list) - 1)
        return frame_list[index]
    
    return VideoClip(make_frame, duration=duration).with_fps(FPS)


# ---------------------------
# Main Script
# ---------------------------
def main():
    # Determine clip title:
    # In debug mode, use the basic title extraction.
    # Otherwise, use ChatGPT (via requests) to get a refined title.
    if DEBUG_MODE:
        title = get_title_from_quote(TEXT_TO_TYPE)
    else:
        title = get_clip_title_using_chatgpt(TEXT_TO_TYPE)
    sanitized_title = sanitize_filename(title)
    
    # Select output folder based on debug mode.
    if DEBUG_MODE:
        output_folder = os.path.join(DEBUG_MODE_OUTPUT_DIR, sanitized_title)
    else:
        output_folder = os.path.join(OUT_BASE_FOLDER, sanitized_title)
    os.makedirs(output_folder, exist_ok=True)
    
    # Define paths for the video, metadata JSON, and temporary audio file.
    output_video_path = os.path.join(output_folder, f"{sanitized_title}.mp4")
    metadata_json_path = os.path.join(output_folder, "metadata.json")
    temp_audio_path = os.path.join(output_folder, "temp_audio.m4a")
    
    # Load and prepare images
    book_cover = load_and_resize_image(IMG_BOOK_COVER_PATH, VIDEO_WIDTH, VIDEO_HEIGHT)
    blank_page_raw = load_and_resize_image(IMG_BLANK_PAGE_PATH, VIDEO_WIDTH, VIDEO_HEIGHT)
    blank_page = create_blank_page_composite(blank_page_raw)

    # Load fonts for the quote and the author text
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()
    try:
        font_author = ImageFont.truetype(FONT_PATH_AUTHOR, FONT_SIZE_AUTHOR)
    except Exception:
        font_author = ImageFont.load_default()

    # Optimization 4: Process the most common static frames in advance
    print("Pre-computing frames to optimize rendering...")
    
    # Create video segments
    clip1 = make_static_clip(book_cover, DURATION_BOOK_COVER)
    transition_clip = make_transition_clip(book_cover, blank_page, DURATION_TRANSITION)
    clip3 = make_static_clip(blank_page, DURATION_BLANK_FREEZE)
    
    print("Generating typing clip frames...")
    typing_clip = make_typing_clip(blank_page, TEXT_TO_TYPE, TYPING_CPS, font)
    
    # Get the final frame with the fully typed quote
    final_text_frame = typing_clip.get_frame(typing_clip.duration)
    
    # Create a 3-second static clip with the quote fully visible
    quote_freeze_clip = make_static_clip(final_text_frame, 3)
    
    # Create author/book typing clip using the final_text_frame as background
    print("Generating author typing clip frames...")
    author_text = f"{chosen_quote['Author']}\n{chosen_quote['Book Title']}"
    author_position = (LEFT_MARGIN, VIDEO_HEIGHT - FONT_SIZE_AUTHOR - 180)
    author_typing_clip = make_typing_clip(
        final_text_frame,
        author_text, 
        TYPING_CPS, 
        font_author, 
        position=author_position, 
        delay_line=0.5
    )
    
    # Get the final frame with both quote and author/book title
    final_complete_frame = author_typing_clip.get_frame(author_typing_clip.duration)
    
    # Create a 5-second freeze with everything visible
    final_freeze_clip = make_static_clip(final_complete_frame, 5)
    
    # Concatenate all segments
    print("Concatenating video segments...")
    final_clip = concatenate_videoclips([
        clip1,                  # Book cover
        transition_clip,        # Transition to blank page
        clip3,                  # Blank page freeze
        typing_clip,            # Quote typing
        quote_freeze_clip,      # 3-second freeze with quote visible
        author_typing_clip,     # Author and book title typing
        final_freeze_clip       # 5-second freeze with everything visible
    ])

    # Optimization 5: Pre-apply ancient effect to key frames to build cache
    print("Applying ancient effect with optimization...")
    apply_ancient_effect(book_cover)
    apply_ancient_effect(blank_page)
    apply_ancient_effect(final_text_frame)
    apply_ancient_effect(final_complete_frame)
    
    def final_make_frame(t):
        frame = final_clip.get_frame(t)
        processed_frame = apply_ancient_effect(frame)
        processed_frame = apply_color_grade(processed_frame)  # Apply cinematic color grade
        # Apply a subtle flicker effect (narrowed brightness variation)
        flicker = random.uniform(0.99, 1.01)
        processed_frame = np.clip(processed_frame * flicker, 0, 255).astype(np.uint8)
        return processed_frame
    
    # Create the final clip with ancient effect, color grading, and flicker
    final_clip_processed = VideoClip(final_make_frame, duration=final_clip.duration).with_fps(FPS)

    # Add typing sound effects
    print("Adding sound effects...")
    T_typing_start = DURATION_BOOK_COVER + DURATION_TRANSITION + DURATION_BLANK_FREEZE
    typing_sound_clips = []
    sound_files = [os.path.join(TYPING_SOUNDS_DIR, f) for f in os.listdir(TYPING_SOUNDS_DIR)
                   if f.lower().endswith(('.mp3', '.wav'))]
    max_text_width = VIDEO_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    typing_schedule = compute_typing_schedule(TEXT_TO_TYPE, TYPING_CPS, font, max_text_width)
    
    if sound_files:
        for i in range(4, len(TEXT_TO_TYPE) + 1, 4):
            if i < len(typing_schedule):
                t_start = T_typing_start + typing_schedule[i-1]
                sound_file = random.choice(sound_files)
                try:
                    sound_clip = AudioFileClip(sound_file)
                    sound_clip = sound_clip.with_start(t_start)
                    typing_sound_clips.append(sound_clip)
                except Exception as e:
                    print(f"Error loading sound {sound_file}: {e}")
                    
    # Add sounds for the author/book title typing
    author_typing_start = T_typing_start + typing_clip.duration + 3
    author_schedule = compute_typing_schedule(author_text, TYPING_CPS, font_author, max_text_width, delay_line=0.5)
    
    if sound_files:
        for i in range(4, len(author_text) + 1, 4):
            if i < len(author_schedule):
                t_start = author_typing_start + author_schedule[i-1]
                sound_file = random.choice(sound_files)
                try:
                    sound_clip = AudioFileClip(sound_file)
                    sound_clip = sound_clip.with_start(t_start)
                    typing_sound_clips.append(sound_clip)
                except Exception as e:
                    print(f"Error loading sound {sound_file}: {e}")
                    
    if typing_sound_clips:
        composite_audio = CompositeAudioClip(typing_sound_clips).with_duration(final_clip_processed.duration)
        final_clip_processed = final_clip_processed.with_audio(composite_audio)

    # Optimization 7: Use multiprocessing for video encoding
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

    # Create metadata JSON
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
    main()
