"""
Matrix_v1 – Animated‑Text Video Creator
======================================
Author: Mr. O3  (OpenAI o3)
Last‑updated: 2025‑04‑21

Purpose
-------
Create short‑form or landscape videos in which text segments either **type‑in** or **fade‑in**, optionally play realistic typing/backspace SFX, overlay a media background, mix in TTS narration, and finish with an outro clip.

Capabilities (high‑level)
------------------------
* Per‑character **typing** animation with variable human‑like speed, cursor, and realistic key/backspace sounds.
* Alternative **fade‑in** appearance with no typing SFX.
* Two “text‑remover” styles after each segment: **backspace** (default) or **fade‑out**.
* Optional flag to **keep the last segment on screen** until the video ends.
* **Language‑aware direction** – each segment is rendered LTR for English or RTL for Hebrew; mixed segments follow the first word.
* Arbitrary list of image/video clips may act as a moving background instead of a solid colour.
* Optional multi‑voice **OpenAI TTS** per segment, stamped onto the timeline.
* Optional background soundtrack, master volume controls, outro clip, transparent overlay, stroke/shadow effects, etc.
* Saves a concise *metadata.json* next to the final MP4 and cleans temp TTS files.

CLI arguments (grouped logically)
---------------------------------
Required
^^^^^^^^
* **--text**               : string – text to animate.
* **--output_path**        : path  – where to write the MP4.

Visuals & colours
^^^^^^^^^^^^^^^^^
* **--fore_color**         : "R,G,B" (default 255,0,0)
* **--bg_color**           : "R,G,B" (default 0,0,0)
* **--font_path**          : path to .ttf (default Windows Arial Blk)
* **--font_size**          : int (40)
* **--font_effect**        : comma‑list of *stroke, shadow, transparent_overlay*
* **--transparent_overlay_effect_color** : "R,G,B,A" (255,255,255,128)

Appearance & removal behaviour
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* **--text_appearance_style** : *type* (default) | fade  ← **NEW**
* **--text_remover_style**    : *backspace* (default) | fadeout
* **--keep_last_segment**     : bool   (False)         ← **NEW**
* **--pause_time**            : seconds between finish‑typing and removal (1.0)
* **--gap_pause**             : seconds gap between segments (1.0)
* **--gap_pause_last_segment**: seconds gap after last segment removal (1.0)

Timing & speed
^^^^^^^^^^^^^^
* **--typing_speed**   : seconds per char (0.05)
* **--fps**            : frames per second (30)
* **--is_short**       : bool – True = 1080×1920, else 1920×1080
* **--enable_cursor_line** : bool – draw rotating/blinking cursor

Audio extras
^^^^^^^^^^^^
* **--typing_sounds_dir** : folder of .mp3 key hits
* **--typing_sounds_volume** : multiplier (1.0)
* **--background_audio_path / _volume**
* **TTS** – **--enable_tts**, **--tts_model**, **--tts_voice**, **--tts_voice_speed**, **--tts_voice_volume**, **--tts_voice_instructions**

Background & outro
^^^^^^^^^^^^^^^^^^
* **--media_paths** : list of images/videos used as background
* **--enable_outro / --outro_mp4_path**

Run `python matrix_v1.py --help` for the complete list.
"""

import re
import random
import argparse
from pathlib import Path
import sys
from moviepy import (
    VideoClip,
    ImageClip,
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_videoclips,
)
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.video.fx.FadeOut import FadeOut
from moviepy.audio.fx import AudioFadeOut
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ---------------------------------------------------------------------------
#  Project‑local modules (OpenAI TTS wrapper)
# ---------------------------------------------------------------------------
Modules_Dir = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Internal_Modules"
sys.path.insert(0, Modules_Dir)
from utilities.request_openai_tts.request_openai_tts import generate_speech
from utilities.json_manager.json_manager import create_json

# ---------------------------------------------------------------------------
#  Helper – language & direction detection
# ---------------------------------------------------------------------------
heb_chars = re.compile(r"[\u0590-\u05FF]")
eng_chars = re.compile(r"[A-Za-z]")

def detect_direction(text: str) -> str:
    """Return 'rtl' if the first *word* contains Hebrew letters, else 'ltr'."""
    for word in text.strip().split():
        if heb_chars.search(word):
            return "rtl"
        if eng_chars.search(word):
            return "ltr"
    return "ltr"  # fallback

# ---------------------------------------------------------------------------
#  Timing helpers
# ---------------------------------------------------------------------------

def compute_timestamps(text: str, base_delay: float, variation_range):
    """Return cumulative per‑char delays to mimic human typing."""
    timestamps = []
    cumulative = 0.0
    for char in text:
        delay = base_delay * random.uniform(*variation_range)
        if char in ".!?":
            delay *= random.uniform(1.5, 2.0)
        elif char == " ":
            delay *= random.uniform(1.2, 1.5)
        cumulative += delay
        timestamps.append(cumulative)
    return timestamps, cumulative

# ---------------------------------------------------------------------------
#  Timeline assembly
# ---------------------------------------------------------------------------

def build_timeline(
    segments,
    base_delay,
    initial_pause,
    gap_pause,
    fade_duration,
    keep_last_segment: bool,
):
    """Return *timeline* list + overall duration."""
    timeline = []
    current_time = initial_pause
    for i, item in enumerate(segments):
        text = item["text"]
        pause_time = item["delay"]
        direction = item["direction"]
        typing_ts, type_duration = compute_timestamps(text, base_delay, (0.98, 1.02))

        segment = {
            "sentence": text,
            "direction": direction,
            "start_typing": current_time,
            "typing_timestamps": typing_ts,
            "end_typing": current_time + type_duration,
            "pause": pause_time,
        }

        is_last = i == len(segments) - 1

        # Decide removal phase based on flags
        if not (is_last and keep_last_segment):
            if text_remover_style == "backspace":
                backspace_delay_per_char = base_delay / 2.0
                backspace_duration = len(text) * backspace_delay_per_char
                segment["start_backspace"] = current_time + type_duration + pause_time
                segment["backspace_duration"] = backspace_duration
                segment["end_backspace"] = segment["start_backspace"] + backspace_duration
                delta = (
                    type_duration
                    + pause_time
                    + backspace_duration
                    + (gap_pause_last_segment if is_last else gap_pause)
                )
            else:  # remover == fadeout
                segment["start_fade"] = current_time + type_duration + pause_time
                segment["fade_duration"] = fade_duration
                segment["end_fade"] = segment["start_fade"] + fade_duration
                delta = (
                    type_duration
                    + pause_time
                    + fade_duration
                    + (gap_pause_last_segment if is_last else gap_pause)
                )
        else:
            # keep last segment on screen – no removal scheduled
            delta = type_duration + pause_time

        timeline.append(segment)
        current_time += delta

    return timeline, current_time

# ---------------------------------------------------------------------------
#  Audio SFX builder
# ---------------------------------------------------------------------------

def create_audio_events(timeline, base_delay):
    """Generate typing/backspace SFX only if **appearance_style == 'type'**."""
    if text_appearance_style != "type":
        return []
    if not typing_sounds_dir or not Path(typing_sounds_dir).exists():
        return []

    audio_files = list(Path(typing_sounds_dir).glob("*.mp3"))
    if not audio_files:
        return []

    get_random_sound = lambda: random.choice(audio_files)
    audio_events = []

    # ---------------- Typing sounds ----------------
    for segment in timeline:
        sentence = segment["sentence"]
        for i in range(0, len(sentence), 2):
            event_time = segment["start_typing"] + segment["typing_timestamps"][i]
            clip_full = AudioFileClip(str(get_random_sound()))
            clip = (
                clip_full.subclipped(0, min(base_delay, clip_full.duration))
                .with_start(event_time)
                .with_effects([MultiplyVolume(factor=typing_sounds_volume)])
            )
            audio_events.append(clip)

    # ---------------- Backspace sounds -------------
    if text_remover_style == "backspace":
        for segment in timeline:
            if "start_backspace" in segment:
                num_chars = len(segment["sentence"])
                back_delay = base_delay / 1.5
                start = segment["start_backspace"]
                total_time = num_chars * back_delay
                for i in range(0, num_chars - 1, 3):
                    event = start + i * back_delay
                    if event > start + total_time:
                        break
                    clip_full = AudioFileClip(str(get_random_sound()))
                    clip = (
                        clip_full.subclipped(0, min(back_delay, clip_full.duration))
                        .with_start(event)
                        .with_effects([MultiplyVolume(factor=typing_sounds_volume)])
                    )
                    audio_events.append(clip)
    return audio_events

# ---------------------------------------------------------------------------
#  Text wrapping helper
# ---------------------------------------------------------------------------

def wrap_text(text, font, draw, max_width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = w if not cur else f"{cur} {w}"
        if (draw.textbbox((0, 0), test, font=font)[2]) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------------------
#  Core frame renderer
# ---------------------------------------------------------------------------

def make_frame(t, timeline, const_y, width, transparent_bg=False):
    """
    Render the frame at time t using the timeline.
    Handles typing or fade‑in appearance, per‑segment LTR/RTL direction,
    text removal (backspace/fadeout), and cursor rendering.
    """
    global last_cursor_position

    # 1. Prepare canvas
    img = Image.new(
        "RGBA" if transparent_bg else "RGB",
        (width, height),
        color=(0, 0, 0, 0) if transparent_bg else bg_color
    )
    draw = ImageDraw.Draw(img)

    # 2. Hebrew fallback font
    hebrew_font = ImageFont.truetype(fr"C:\Windows\Fonts\arial.ttf", font_size)

    # 3. Find active segment & branch
    selected_segment = None
    branch = None
    fade_factor = 1.0
    progress = 0.0
    prev_backspace_done = False

    for i, seg in enumerate(timeline):
        # detect gap after backspace
        if i > 0 and text_remover_style == "backspace":
            prev = timeline[i-1]
            if prev.get("end_backspace") and prev["end_backspace"] <= t < seg["start_typing"]:
                prev_backspace_done = True

        if t < seg["start_typing"]:
            break

        if seg["start_typing"] <= t < seg["end_typing"]:
            selected_segment = seg
            branch = "typing"
            progress = (t - seg["start_typing"]) / (seg["end_typing"] - seg["start_typing"])
        else:
            if text_remover_style == "backspace":
                if t < seg.get("start_backspace", float("inf")):
                    selected_segment = seg
                    branch = "hold"
                elif seg.get("start_backspace") and seg["start_backspace"] <= t < seg["end_backspace"]:
                    selected_segment = seg
                    branch = "backspace"
                    progress = (t - seg["start_backspace"]) / seg["backspace_duration"]
                else:
                    selected_segment = seg
                    branch = "none"
            else:
                if t < seg.get("start_fade", float("inf")):
                    selected_segment = seg
                    branch = "hold"
                elif seg.get("start_fade") and seg["start_fade"] <= t < seg["end_fade"]:
                    selected_segment = seg
                    branch = "fade"
                    fade_factor = 1.0 - (t - seg["start_fade"]) / seg["fade_duration"]
                else:
                    selected_segment = seg
                    branch = "none"

    # 4. Choose font now that segment is known
    current_font = hebrew_font if selected_segment and selected_segment.get("direction") == "rtl" else font

    # 5. Text metrics & cursor template
    ascent, descent = current_font.getmetrics()
    line_height = ascent + descent
    centered_y = (height - line_height) / 2
    cursor_info = {
        "should_render": enable_cursor_line,
        "is_typing": False,
        "position": (width // 2, centered_y) if last_cursor_position is None else last_cursor_position,
        "has_text": False,
        "just_finished_backspace": False,
    }

    # 6. Nothing to draw?
    if not selected_segment or branch == "none":
        if enable_cursor_line and not prev_backspace_done:
            render_cursor(img, t, cursor_info, current_font, transparent_bg)
            last_cursor_position = cursor_info["position"]
        return np.array(img)

    # 7. Wrap & reveal text
    full_text = selected_segment["sentence"]
    direction = selected_segment["direction"]
    max_w = int(width * 0.9)
    lines = wrap_text(full_text, current_font, draw, max_w)
    total_h = line_height * len(lines)
    y_start = (height - total_h) / 2

    if branch == "typing":
        if text_appearance_style == "type":
            revealed = int(progress * len(full_text))
        else:
            revealed = len(full_text)
            fade_factor = progress
    elif branch == "backspace":
        revealed = max(0, len(full_text) - int(progress * len(full_text)))
    else:
        revealed = len(full_text)

    rem = revealed
    drawn = []
    for line in lines:
        if rem >= len(line):
            drawn.append(line)
            rem -= len(line)
        else:
            rem = revealed
            drawn = []
            for line in lines:
                if rem >= len(line):
                    drawn.append(line)
                    rem -= len(line)
                else:
                    # avoid the “-0” pitfall: compute start index explicitly
                    if direction == "rtl":
                        start_idx = len(line) - rem
                        part = line[start_idx:]    # reveals from the right
                    else:
                        part = line[:rem]          # reveals from the left
                    drawn.append(part)
                    rem = 0
    drawn += [""] * (len(lines) - len(drawn))

    # 8. Draw lines
    effects = [e.strip() for e in font_effect.split(",") if e.strip()]
    last_vis = last_x = last_y = last_w = None
    for idx, line in enumerate(lines):
        full_bbox = draw.textbbox((0, 0), line, font=current_font)
        full_w = full_bbox[2] - full_bbox[0]
        x = (width - full_w) / 2
        y = y_start + idx * line_height
        part = drawn[idx]
        part_w = draw.textbbox((0, 0), part, font=current_font)[2] if part else 0

        if part:
            last_vis = part
            last_y = y
            last_w = part_w
            last_x = x + (full_w - part_w) if direction == "rtl" else x

        # Color + fade logic
        if branch == "fade" or (text_appearance_style == "fade" and branch == "typing"):
            if transparent_bg:
                col = (*fore_color, int(255 * fade_factor))
            else:
                col = tuple(int(c * fade_factor) for c in fore_color)
        else:
            col = (*fore_color, 255) if transparent_bg else fore_color

        # Overlay effect
        if "transparent_overlay" in effects and part and not (branch == "fade" and fade_factor < 0.2):
            m = 5
            overlay_color = tuple(map(int, transparent_overlay_effect_color.split(",")))
            if len(overlay_color) == 3:
                overlay_color = (*overlay_color, 128)
            x_overlay = x + (full_w - part_w) if direction == "rtl" else x
            draw.rectangle([x_overlay - m, y - m, x_overlay + part_w + m, y + line_height + m], fill=overlay_color)

        # Stroke / shadow / base draw
        x_draw = x + (full_w - part_w) if direction == "rtl" else x
        if "stroke" in effects:
            neg = tuple(255 - c for c in fore_color)
            draw.text((x_draw, y), part, font=current_font, fill=col, stroke_width=2, stroke_fill=neg)
        else:
            if "shadow" in effects:
                shadow = (0, 0, 0, 255) if transparent_bg else (0, 0, 0)
                draw.text((x_draw + 2, y + 2), part, font=current_font, fill=shadow)
            draw.text((x_draw, y), part, font=current_font, fill=col)

    # 9. Cursor
    if last_vis:
        if direction == "rtl":
            cursor_info["position"] = (last_x - font_size // 6, last_y)
        else:
            cursor_info["position"] = (last_x + last_w + font_size // 6, last_y)
    if enable_cursor_line:
        render_cursor(img, t, cursor_info, current_font, transparent_bg)
        last_cursor_position = cursor_info["position"]

    return np.array(img)


# ---------------------------------------------------------------------------
#  Cursor renderer
# ---------------------------------------------------------------------------

def render_cursor(img, t, cursor_info, font, transparent_bg=False):
    draw = ImageDraw.Draw(img)
    cursor_chars = "|/-\\"

    if not cursor_info["should_render"]:
        return

    if cursor_info["is_typing"]:
        cur_sym = "|" if text_appearance_style == "type" else " "
    else:
        cur_sym = cursor_chars[int((t * 8) % len(cursor_chars))]

    col = (*fore_color, 255) if transparent_bg else fore_color
    draw.text(cursor_info["position"], cur_sym, font=font, fill=col)

# ---------------------------------------------------------------------------
#  Main orchestrator
# ---------------------------------------------------------------------------

def main(text_content, output_path):
    global width, height, font, fore_color, bg_color

    width, height = ((1080, 1920) if is_short else (1920, 1080))
    font = ImageFont.truetype(str(font_path), font_size)

    base_char_time = typing_speed
    initial_pause = 1.0

    # -------- 1. Split text into segments --------
    split_pattern = r"(?<!\d)([.!?;])(?!\d)" if not separate_by_comma else r"(?<!\d)([.,!?;])(?!\d)"
    parts = re.split(split_pattern, text_content)

    segments_raw = []
    buf = ""
    for part in parts:
        if (part == "," and separate_by_comma) or part in ".;":
            segments_raw.append(buf.strip())
            buf = ""
        elif part in "!?":
            buf += part
            segments_raw.append(buf.strip())
            buf = ""
        else:
            buf += part
    if buf.strip():
        segments_raw.append(buf.strip())

    segments = []
    for s in segments_raw:
        s_no_commas = re.sub(r"[.,]", "", s)
        if len(s_no_commas) < 3:
            continue
        segments.append({
            "text": s_no_commas,
            "delay": pause_time,
            "direction": detect_direction(s_no_commas),
        })

    if not segments:
        raise ValueError("No valid text segments found.")

    # -------- 2. Build timeline --------
    timeline, total_duration = build_timeline(
        segments,
        base_char_time,
        initial_pause,
        gap_pause,
        1.0,
        keep_last_segment,
    )

    # -------- 3. Generate TTS (optional) --------
    tts_audio_segments = []
    if enable_tts:
        tts_temp_dir = Path(output_path).parent / "tts_temp"
        tts_temp_dir.mkdir(exist_ok=True)
        for seg in segments:
            text = seg["text"]
            fname = re.sub(r"[^\w\- ]", "", text)[:40].strip().replace(" ", "_")
            tts_path = tts_temp_dir / f"{fname}.mp3"
            tts_kwargs = {
                "text": text,
                "voice": tts_voice,
                "output_file": str(tts_path),
                "speed": tts_voice_speed or "1.0",
                "instructions": tts_voice_instructions,
            }
            if tts_model:
                tts_kwargs["model"] = tts_model
            generate_speech(**{k: v for k, v in tts_kwargs.items() if v is not None})

        # Align clips to timeline
        for seg in timeline:
            fname = re.sub(r"[^\w\- ]", "", seg["sentence"])[:40].strip().replace(" ", "_")
            p = Path(output_path).parent / "tts_temp" / f"{fname}.mp3"
            if p.exists():
                clip = (
                    AudioFileClip(str(p))
                    .with_start(seg["start_typing"])
                    .with_effects([MultiplyVolume(factor=tts_voice_volume)])
                )
                tts_audio_segments.append(clip)

    # -------- 4. Build audio layers --------
    audio_events = create_audio_events(timeline, base_char_time)
    if audio_events or tts_audio_segments:
        composite_audio = CompositeAudioClip(audio_events + tts_audio_segments)
    else:
        composite_audio = None  # No audio layers


    if background_audio_path and Path(background_audio_path).exists():
        bg_aud = (
            AudioFileClip(background_audio_path)
            .with_duration(total_duration)
            .with_effects([MultiplyVolume(factor=background_audio_volume)])
        )
        composite_audio = (
            CompositeAudioClip([bg_aud]) if composite_audio is None else CompositeAudioClip([composite_audio, bg_aud])
        )

    # -------- 5. Build visuals --------
    if media_paths:
        n_media = len(media_paths)
        base_dur = total_duration / n_media
        deltas = [random.uniform(-1, 1) for _ in range(n_media - 1)] + [0]
        durations = []
        prev = 0
        for d in deltas:
            durations.append(base_dur + d - prev)
            prev = d
        media_clips = []
        for path, dur in zip(media_paths, durations):
            ext = Path(path).suffix.lower()
            if ext in {".mp4", ".mov", ".avi", ".mkv"}:
                vid = VideoFileClip(path)
                start = random.uniform(0, max(0, vid.duration - dur)) if vid.duration > dur else 0
                clip = vid.subclipped(start, start + dur)
            else:
                clip = ImageClip(path).with_duration(dur)
            media_clips.append(clip.resized((width, height)))
        background = concatenate_videoclips(media_clips)
        text_clip = (
            VideoClip(lambda t: make_frame(t, timeline, None, width, transparent_bg=True), duration=total_duration,)
            .with_fps(fps)
        )
        final_clip = CompositeVideoClip([background, text_clip], size=(width, height))
    else:
        final_clip = VideoClip(lambda t: make_frame(t, timeline, None, width), duration=total_duration).with_fps(fps)

    if composite_audio:
        final_clip = final_clip.with_audio(composite_audio)

    # -------- 6. Outro (optional) --------
    if enable_outro and outro_mp4_path and Path(outro_mp4_path).exists():
        fade_dur = 1.0
        final_clip = FadeOut(duration=fade_dur).apply(final_clip)
        if final_clip.audio:
            final_clip = final_clip.with_audio(AudioFadeOut(duration=fade_dur).apply(final_clip.audio))
        outro_clip = VideoFileClip(outro_mp4_path).resized((width, height)).with_fps(fps)
        final_clip = concatenate_videoclips([final_clip, outro_clip], method="compose")

    # -------- 7. Write video & metadata --------
    video_path = Path(output_path)
    video_path.parent.mkdir(parents=True, exist_ok=True)
    final_clip.write_videofile(str(video_path))
    
    json_title = segments[0]['text'] if segments else ""
    json_description = " ".join([s['text'] for s in segments])
    json_output_dir = Path(output_path).parent
    create_json(json_title, json_description, json_output_dir)

    # -------- 8. Cleanup --------
    if enable_tts:
        for f in (audio_path for audio_path in tts_temp_dir.glob("*.mp3")):
            f.unlink()
        tts_temp_dir.rmdir()

    print("Video creation completed:", video_path)

# ---------------------------------------------------------------------------
#  Entry‑point (CLI)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matrix_v1 Video Creator – generates typing/fade‑in text videos.")

    # --- Mandatory ---
    parser.add_argument("--text", required=True, help="Input text content to animate.")
    parser.add_argument("--output_path", required=True, help="Full path for the output video file.")

    # --- Colours / font ---
    parser.add_argument("--fore_color", default="255,0,0", help="Foreground text colour as R,G,B")
    parser.add_argument("--bg_color", default="0,0,0", help="Background colour as R,G,B")
    parser.add_argument("--font_path", default=r"C:\\Windows\\Fonts\\ariblk.ttf", help="Path to the .ttf font file")
    parser.add_argument("--font_size", type=int, default=40, help="Font size")
    parser.add_argument("--font_effect", default="", help="Comma‑separated effects: stroke, shadow, transparent_overlay")
    parser.add_argument("--transparent_overlay_effect_color", default="255,255,255,128", help="RGBA for overlay")

    # --- Behaviour ---
    parser.add_argument("--text_remover_style", default="backspace", help="How to remove previous segment: backspace|fadeout")
    parser.add_argument("--text_appearance_style", default="type", choices=["type", "fade"], help="How each segment appears: type|fade")
    parser.add_argument("--keep_last_segment", type=lambda s: s.lower() in {"true", "1", "yes"}, default=False, help="Keep the last segment visible until video end")

    # --- Timing ---
    parser.add_argument("--pause_time", type=float, default=1.0, help="Pause (s) after segment typed before removal")
    parser.add_argument("--gap_pause", type=float, default=1.0, help="Gap (s) between segments")
    parser.add_argument("--gap_pause_last_segment", type=float, default=1.0, help="Gap after last removal when not kept")
    parser.add_argument("--typing_speed", type=float, default=0.05, help="Seconds per character")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--is_short", type=lambda s: s.lower() in {"true", "1", "yes"}, default=True, help="Vertical (True) or horizontal video")
    parser.add_argument("--enable_cursor_line", type=lambda s: s.lower() in {"true", "1", "yes"}, default=False, help="Show cursor line")

    # --- Sounds ---
    parser.add_argument("--typing_sounds_dir", default=None, help="Directory with typing SFX mp3s")
    parser.add_argument("--typing_sounds_volume", type=float, default=1.0, help="Typing SFX volume multiplier")
    parser.add_argument("--background_audio_path", default=None, help="Background soundtrack")
    parser.add_argument("--background_audio_volume", type=float, default=1.0, help="Background soundtrack volume multiplier")

    # --- TTS ---
    parser.add_argument("--enable_tts", type=lambda s: s.lower() in {"true", "1", "yes"}, default=False, help="Enable OpenAI TTS")
    parser.add_argument("--tts_model", default=None)
    parser.add_argument("--tts_voice", default=None)
    parser.add_argument("--tts_voice_speed", default=None)
    parser.add_argument("--tts_voice_volume", type=float, default=5.0)
    parser.add_argument("--tts_voice_instructions", default=None)

    # --- Background / media ---
    parser.add_argument("--media_paths", nargs="*", default=None, help="List of image/video paths as moving background")

    # --- Outro ---
    parser.add_argument("--enable_outro", type=lambda s: s.lower() in {"true", "1", "yes"}, default=False)
    parser.add_argument("--outro_mp4_path", default=None)

    # --- Misc ---
    parser.add_argument("--separate_by_comma", type=lambda s: s.lower() in {"true", "1", "yes"}, default=True, help="Treat comma as segment separator")

    args = parser.parse_args()

    # Parse simple values
    text_content = args.text
    fore_color = tuple(map(int, args.fore_color.split(",")))
    bg_color = tuple(map(int, args.bg_color.split(",")))
    output_path = args.output_path
    text_remover_style = args.text_remover_style.lower()
    text_appearance_style = args.text_appearance_style.lower()
    keep_last_segment = args.keep_last_segment
    typing_sounds_dir = args.typing_sounds_dir
    typing_sounds_volume = args.typing_sounds_volume
    background_audio_path = args.background_audio_path
    background_audio_volume = args.background_audio_volume
    font_path = args.font_path
    font_size = args.font_size
    fps = args.fps
    is_short = args.is_short
    pause_time = args.pause_time
    typing_speed = args.typing_speed
    media_paths = args.media_paths or []
    font_effect = args.font_effect
    transparent_overlay_effect_color = args.transparent_overlay_effect_color
    enable_tts = args.enable_tts
    tts_model = args.tts_model
    tts_voice = args.tts_voice
    tts_voice_speed = args.tts_voice_speed
    tts_voice_volume = args.tts_voice_volume
    tts_voice_instructions = args.tts_voice_instructions
    separate_by_comma = args.separate_by_comma
    enable_outro = args.enable_outro
    outro_mp4_path = args.outro_mp4_path
    gap_pause = args.gap_pause
    gap_pause_last_segment = args.gap_pause_last_segment
    enable_cursor_line = args.enable_cursor_line
    last_cursor_position = None

    print("[Matrix_v1] Starting video creation…")
    main(text_content, output_path)
