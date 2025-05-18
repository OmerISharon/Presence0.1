import os
import random
import subprocess
import datetime
import sys

# Setup project modules path
Modules_Dir = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Internal_Modules"
sys.path.insert(0, Modules_Dir)

from utilities.request_chatgpt.request_chatgpt import request_chatgpt_response
from utilities.get_pexels_media.get_pexels_media import download_pexels_media

debug_mode = True  # Set to False to enable real ChatGPT API call

# ──────────────────────────────────────────────────────────────
# Step 1: Global variables
# ──────────────────────────────────────────────────────────────

output_dir = fr"D:\2025\Projects\Presence\Presence0.1\Channels\ASMRelax\Clips"
background_music_dir = fr"D:\2025\Projects\Presence\Presence0.1\Creator\Channels\ASMRelax\Resources\ASMR Sounds"
matrix_script_path = fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules\creators\matrix\matrix_v1\matrix_v1.py"
selected_voice = "nova"

# ──────────────────────────────────────────────────────────────
# Step 2: Generate prompts for ChatGPT
# ──────────────────────────────────────────────────────────────

system_prompt = (
    "You are a calming and gentle ASMR-style narrator. "
    "Your goal is to generate short, peaceful, and relaxing sentences that feel soothing to hear. "
    "Each output should be broken into 3 to 5 natural narration segments, with each segment ending in a period ('.') to guide ASMR pacing. "
    "Avoid commas — use only periods to separate each calm, self-contained thought. "
    "Keep the vocabulary simple. The tone should be soft, dreamy, and comforting. "
    "Avoid intensity, complexity, or anything too energetic. "
    "Every sentence should feel like a warm whisper of peace, perfect for quiet ASMR narration."
)

user_prompt = (
    "Write a calming and relaxing whisper-style message. "
    "Keep it gentle, peaceful, and simple. "
    "Break it into 3 to 5 natural narration segments using periods (.) only — no commas for rhythm. "
    "Each beat should be its own standalone sentence or thought. Make it feel snappy and voiceover-ready."
)

# ──────────────────────────────────────────────────────────────
# Step 2: Generate instructions for OPENAI tts module
# ──────────────────────────────────────────────────────────────

tts_base_instructions = """Voice: Soft, gentle, and whisper-like, creating a soothing and intimate atmosphere.

Tone: Calm and nurturing, with a peaceful rhythm that promotes relaxation and comfort.

Punctuation: Use short sentences and clear pauses. End each thought with a subtle stop to maintain a tranquil flow.

Delivery: Slow and delicate, with a smooth cadence. Emphasize softness over clarity, like a warm breeze in the background."""

# ──────────────────────────────────────────────────────────────
# Step 3: Get ChatGPT response
# ──────────────────────────────────────────────────────────────
if debug_mode:
    text = "The room is quiet. The light is soft. Your body feels warm. Your breath is slow. Everything is okay."
else:
    text, vibe, response_subject, tags = request_chatgpt_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        vibe_needed=False,
        subject_needed=False,
        tags_needed=False,
        max_tokens=200
    )

    if not text:
        print("No response text received. Exiting.")
        sys.exit(1)

print("ChatGPT Text:", text)
# ──────────────────────────────────────────────────────────────
# Step 4: Prepare output folders
# ──────────────────────────────────────────────────────────────

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
base_output_dir = fr"{output_dir}\{timestamp}"
resources_dir = os.path.join(base_output_dir, "resources")
os.makedirs(resources_dir, exist_ok=True)

# ──────────────────────────────────────────────────────────────
# Step 5: Choose background music
# ──────────────────────────────────────────────────────────────

directory = background_music_dir
mp3_files = [f for f in os.listdir(directory) if f.lower().endswith('.mp3')]

if not mp3_files:
    raise FileNotFoundError("No MP3 files found in the Inspirational folder.")

background_music =  os.path.join(directory, random.choice(mp3_files))

# ──────────────────────────────────────────────────────────────
# Step 6: Download media from Pexels using tags
# ──────────────────────────────────────────────────────────────

tags = ["Relax", "Landscape", "Chill"]
media_paths = []

for tag in tags:
    print(f"Downloading vertical media for tag: {tag}")
    try:
        tag_output_dir = os.path.join(resources_dir, tag)
        media_count = 1  # always 1 video per tag

        # Download 1 vertical video from Pexels for the current tag
        download_pexels_media(subject=tag, media_count=media_count, output_dir=tag_output_dir)

        # If directory exists, add the .mp4 file to media_paths
        if os.path.exists(tag_output_dir):
            mp4_files = [f for f in os.listdir(tag_output_dir) if f.lower().endswith(".mp4")]
            if mp4_files:
                chosen_video = random.choice(mp4_files)
                media_paths.append(os.path.join(tag_output_dir, chosen_video))

    except Exception as e:
        print(f"❌ Failed to download media for tag '{tag}': {e}")

# ──────────────────────────────────────────────────────────────
# Step 7: Set the gap_pause
# ──────────────────────────────────────────────────────────────

# Count segments (each ends with a period)
segments = [s.strip() for s in text.split(".") if s.strip()]
segment_count = len(segments)

# Ensure there’s at least one segment
if segment_count == 0:
    raise ValueError("No segments detected in the text.")

# Average duration per segment
average_segment_duration = 60 / segment_count

# Example output
print(f"Segment count: {segment_count}")
print(f"Average segment duration: {average_segment_duration:.2f} seconds")


# ──────────────────────────────────────────────────────────────
# Step 8: Build arguments for matrix_v1.py
# ──────────────────────────────────────────────────────────────

matrix_args = [
    "python", matrix_script_path,
    "--text", text,
    "--output_path", os.path.join(base_output_dir, f"{timestamp}.mp4"),
    "--fore_color", "0,0,0",
    "--text_remover_style", "fadeout",
    "--text_appearance_style", "fade",
    "--background_audio_path", background_music,
    "--background_audio_volume", "1.0",
    "--typing_sounds_volume", "0.2",
    "--font_size", "64",
    "--font_effect", "transparent_overlay",
    "--transparent_overlay_effect_color", "251, 222, 94, 150",
    "--enable_tts", "true",
    "--tts_voice", selected_voice,
    "--tts_voice_instructions", tts_base_instructions,
    "--separate_by_comma", "False",
    "--enable_outro", "True",
    "--pause_time", "2.0",
    "--gap_pause", "2.0",
    "--gap_pause_last_segment", "3.0"
]

# Add media_paths to matrix_args if any were found
if media_paths:
    matrix_args.extend(["--media_paths"])
    matrix_args.extend(media_paths)

print(matrix_args)

print("Running matrix_v1.py to generate the video...")
subprocess.run(matrix_args)