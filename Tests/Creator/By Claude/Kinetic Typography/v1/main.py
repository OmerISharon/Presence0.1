#!/usr/bin/env python3
"""
Kinetic Typography Video Generator

Special Characters in the input text:
  '.'  : Removed from the displayed text and causes a pause. Each '.' adds a skip of SPECIAL_BEAT_SKIP_VALUES['.'] beats.
  '*'  : Removed from the displayed text and toggles the foreground (text) and background colors.
         A subsequent '*' toggles the colors back.
  '&'  : Removed from the displayed text and triggers a pop-in effect (sizing and fade-in animation)
         on the word. Each '&' adds a skip of SPECIAL_BEAT_SKIP_VALUES['&'] beats.
  '!'  : Removed from the displayed text and triggers a side-slide effect, where the word enters from the side,
         overshoots the center, and then settles back to the center. Each '!' adds a skip of SPECIAL_BEAT_SKIP_VALUES['!'] beats.
  '^'  : Removed from the displayed text and triggers a rotation effect.
         The word rotates from an initial angle (e.g. 20°) to 0° over the effect duration.
         
Usage:
    python main.py "Your text here with special characters like . * & ! ^" [--uppercase]
"""

import argparse
import re
import os
import sys
from moviepy import CompositeVideoClip, TextClip, AudioFileClip, concatenate_audioclips

from config import *
from bpm_detector import detect_beats
from effects_config import *
from typographic_effects import *
from get_content import *


def create_kinetic_typography_video(input_text: str, force_uppercase: bool = False) -> None:

    """
    Create a kinetic typography video from input text using beat timings detected
    from the background audio file. Special characters are processed as follows:
      - '.' causes a pause by skipping beats and is removed from the displayed text.
      - '*' toggles the foreground and background colors.
      - '&' triggers a pop-in effect and causes a pause by skipping beats.
      - '!' triggers a side-slide effect and causes a pause by skipping beats.
      - '^' triggers a rotation effect and causes a pause by skipping beats.
      (The number of beats to skip is determined by SPECIAL_BEAT_SKIP_VALUES.)

    Args:
        input_text (str): The input text to be animated (allowed: letters, digits, spaces, '.', '*', '&', '!').
        force_uppercase (bool): If True, converts all displayed words to uppercase.
    """

    print("Step 1: Parsing text into tokens and processing special characters.")
    raw_tokens = input_text.split()
    tokens = []  # List of dictionaries for each token
    # Initialize current color state from configuration.
    current_text_color = TEXT_COLOR
    current_bg_color = BACKGROUND_COLOR

    for raw_word in raw_tokens:
        # Count special characters as flags (0 if absent, 1 if present)
        period_flag = 1 if '.' in raw_word else 0
        ampersand_flag = 1 if '&' in raw_word else 0
        exclamation_flag = 1 if '!' in raw_word else 0
        rotation_flag = 1 if '^' in raw_word else 0
        
        # Calculate total skip beats based on the flags and SPECIAL_BEAT_SKIP_VALUES
        skip_beats = (period_flag * SPECIAL_BEAT_SKIP_VALUES.get('.', DEFAULT_BEAT_SKIP_VALUE) +
                    ampersand_flag * SPECIAL_BEAT_SKIP_VALUES.get('&', DEFAULT_BEAT_SKIP_VALUE) +
                    exclamation_flag * SPECIAL_BEAT_SKIP_VALUES.get('!', DEFAULT_BEAT_SKIP_VALUE) +
                    rotation_flag * SPECIAL_BEAT_SKIP_VALUES.get('^', DEFAULT_BEAT_SKIP_VALUE))
        
        # Count '*' for toggling colors (do not contribute to skip beats).
        star_count = raw_word.count('*')
        
        # Remove special characters from the displayed text.
        word = raw_word.replace('*', '').replace('.', '').replace('&', '').replace('!', '').replace('^', '')
        
        # Toggle colors if an odd number of '*' is found.
        if star_count % 2 == 1:
            current_text_color, current_bg_color = current_bg_color, current_text_color
        
        if force_uppercase:
            word = word.upper()
        
        # Set flags for the various effects.
        # Set flags for the various effects (0 or 1 logic used above)
        side_slide = exclamation_flag == 1
        pop_in = ampersand_flag == 1
        rotate = rotation_flag == 1
        
        tokens.append({
            "text": word,
            "skip_beats": skip_beats,
            "pop_in": pop_in,
            "side_slide": side_slide,
            "rotate": rotate,
            "text_color": current_text_color,
            "bg_color": current_bg_color
        })

    print(f"  Tokens: {tokens}")

    # Calculate total beats needed.
    # Each token uses 1 beat for its appearance plus additional skip_beats.
    total_beats_needed = sum(1 + token["skip_beats"] for token in tokens)
    print(f"  Total beats needed: {total_beats_needed}")

    print("Step 2: Detecting beats from background audio.")
    try:
        tempo, beat_times = detect_beats(BACKGROUND_AUDIO_PATH)
        beat_times = [t / WORD_SPEED_FACTOR for t in beat_times]
        print(f"  Detected BPM: {tempo}")
        print(f"  Initial beat times (count={len(beat_times)}): {beat_times}")
    except Exception as e:
        print(f"Error detecting beats: {e}", file=sys.stderr)
        sys.exit(1)

    # Extend beat_times if needed.
    if len(beat_times) < total_beats_needed:
        print("  Not enough beat times detected. Extending beat_times...")
        if len(beat_times) > 1:
            avg_interval = (beat_times[-1] - beat_times[0]) / (len(beat_times) - 1)
        else:
            avg_interval = 1.0
        needed = total_beats_needed - len(beat_times)
        extension_start = beat_times[-1] if beat_times else 0
        extended = [extension_start + avg_interval * (i + 1) for i in range(needed)]
        beat_times.extend(extended)
        print(f"  Extended beat times (count={len(beat_times)}): {beat_times}")
    else:
        print("  Sufficient beat times detected; no extension needed.")

    print("Step 3: Creating text clips with proper timing and effects.")
    current_index = 0  # Index into beat_times list
    video_clips = []

    for token in tokens:
        start_time = beat_times[current_index]
        # New duration calculation: sum the durations of the current beat and the next skip_beats.
        end_index = current_index + token["skip_beats"] + 1
        if end_index < len(beat_times):
            duration = beat_times[end_index] - beat_times[current_index]
        else:
            duration = 1.0

        if token["text"].strip():
            # For tokens with side slide, process that effect.
            if token.get("side_slide", False):
                txt_clip = TextClip(
                    text=token["text"],
                    font_size=FONT_SIZE,
                    color=token["text_color"],
                    font=FONT_PATH,
                    size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                    method='caption',
                    bg_color=token["bg_color"]
                ).with_start(start_time).with_duration(duration)
                movement_duration = beat_times[current_index + 1] - beat_times[current_index] if (current_index + 1) < len(beat_times) else 1.0
                txt_clip = apply_side_slide_effect(txt_clip, effect_duration=movement_duration, overshoot=50)
            # Else if token has rotation effect.
            elif token.get("rotate", False):
                txt_clip = TextClip(
                    text=token["text"],
                    font_size=FONT_SIZE,
                    color=token["text_color"],
                    font=FONT_PATH,
                    size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                    method='caption',
                    bg_color=token["bg_color"]
                ).with_position('center').with_start(start_time).with_duration(duration)
                # Apply rotation effect using the base beat duration as the effect duration.
                movement_duration = beat_times[current_index + 1] - beat_times[current_index] if (current_index + 1) < len(beat_times) else 1.0
                txt_clip = apply_rotation_effect(txt_clip, effect_duration=movement_duration, initial_angle=ROTATION_INITIAL_ANGLE)
            else:
                # Default: no side slide or rotation.
                txt_clip = TextClip(
                    text=token["text"],
                    font_size=FONT_SIZE,
                    color=token["text_color"],
                    font=FONT_PATH,
                    size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                    method='caption',
                    bg_color=token["bg_color"]
                ).with_position('center').with_start(start_time).with_duration(duration)
                if token["pop_in"]:
                    txt_clip = apply_pop_in_effect(txt_clip, pop_duration=POP_IN_DURATION)
            video_clips.append(txt_clip)
        else:
            print(f"  (No text clip for an empty token; skip_beats={token['skip_beats']})")
        current_index += 1 + token["skip_beats"]

    if video_clips:
        last_clip = video_clips[-1]
        final_duration = last_clip.start + last_clip.duration
    else:
        final_duration = 0.0
    print(f"  Final video duration computed as: {final_duration:.3f} seconds")

    print("Step 4: Composing the final video clip.")
    final_video = CompositeVideoClip(
        video_clips,
        size=(VIDEO_WIDTH, VIDEO_HEIGHT),
        bg_color=BACKGROUND_COLOR
    ).with_duration(final_duration)

    print("Step 5: Processing background audio.")
    audio = None
    try:
        audio = AudioFileClip(BACKGROUND_AUDIO_PATH)
        print(f"  Original audio duration: {audio.duration:.3f} seconds")
        if audio.duration < final_duration:
            nloops = int(final_duration // audio.duration) + 1
            print(f"  Audio is shorter than video duration. Looping audio {nloops} times.")
            audio_clips = [audio for _ in range(nloops)]
            looped_audio = concatenate_audioclips(audio_clips)
            audio = looped_audio.subclipped(0, final_duration)
            print(f"  Loop-extended audio duration: {audio.duration:.3f} seconds")
        else:
            audio = audio.subclipped(0, final_duration)
            print(f"  Trimmed audio duration: {audio.duration:.3f} seconds")
        final_video = final_video.with_audio(audio)
    except Exception as e:
        print(f"Error processing audio: {e}")
        print("  Video will be created without background audio.")

    print("Step 6: Ensuring output directory exists.")
    os.makedirs(os.path.dirname(OUTPUT_VIDEO_PATH), exist_ok=True)
    print(f"  Output directory: {os.path.dirname(OUTPUT_VIDEO_PATH)}")

    print("Step 7: Writing the final video file.")
    final_video.write_videofile(OUTPUT_VIDEO_PATH, fps=VIDEO_FPS)
    print(f"Kinetic typography video created: {OUTPUT_VIDEO_PATH}")

    # Cleanup
    final_video.close()
    if audio is not None:
        audio.close()


def main():
    parser = argparse.ArgumentParser(
        description="Create a kinetic typography video from user-supplied text."
    )
    parser.add_argument("text", help="The text to be animated.")
    parser.add_argument(
        "--uppercase",
        action="store_true",
        help="Convert all words to uppercase."
    )
    args = parser.parse_args()

    cleaned_text = re.sub(r"[^a-zA-Z0-9.*&! ]", "", args.text)

    print("Starting kinetic typography video creation.")
    create_kinetic_typography_video(cleaned_text, force_uppercase=args.uppercase)
    print("Video creation process complete.")

if __name__ == "__main__":
    main()
