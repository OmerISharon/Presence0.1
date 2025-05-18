import os
import random
import subprocess
import datetime
import sys

import config

# Setup project modules path
Modules_Dir = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Internal_Modules"
sys.path.insert(0, Modules_Dir)

from utilities.request_chatgpt.request_chatgpt import request_chatgpt_response
from utilities.get_pexels_media.get_pexels_media import run_pexels_download as download_pexels_media
from subjects import fun_fact_subjects

debug_mode = False  # Set to False to enable real ChatGPT API call

# ──────────────────────────────────────────────────────────────
# Step 1: Choose a random fun fact subject and a random tts voice
# ──────────────────────────────────────────────────────────────

subject = random.choice(fun_fact_subjects)

selected_voice = "nova"

# ──────────────────────────────────────────────────────────────
# Step 2: Generate prompts for ChatGPT
# ──────────────────────────────────────────────────────────────

system_prompt = (
    "You are an expert fun fact storyteller for voiceover videos. Your goal is to deliver short, surprising, "
    "and highly engaging fun facts that are perfect for narration. Each fun fact must be broken into short, natural segments, "
    "with each segment ending in a literal period ('.') to guide pacing and voiceover flow. "
    "Avoid commas for pauses — use periods only to separate each natural beat. "
    "Limit the total number of segments to about 3 to 5, so the fact feels punchy and doesn't ramble. "
    "Every sentence should feel delightful, info-rich, and easy to read aloud."
)


user_prompt = (
    f"Give me a unique, surprising, and short fun fact about {subject}. "
    "Break it into 3 to 5 natural narration segments using periods (.) only — no commas for rhythm. "
    "Each beat should be its own standalone sentence or thought. Make it feel snappy and voiceover-ready."
)

# ──────────────────────────────────────────────────────────────
# Step 2: Generate instructions for OPENAI tts module
# ──────────────────────────────────────────────────────────────

tts_base_instructions = """Voice: Clear, authoritative, and composed, projecting confidence and professionalism.

Tone: Neutral and informative, maintaining a balance between formality and approachability.

Punctuation: Structured with commas and pauses for clarity, ensuring information is digestible and well-paced.

Delivery: Steady and measured, with slight emphasis on key figures and deadlines to highlight critical points."""

# ──────────────────────────────────────────────────────────────
# Step 3: Get ChatGPT response
# ──────────────────────────────────────────────────────────────
if debug_mode:
    text = "Our Milky Way has a sibling. Andromeda Galaxy is on a collision course with it. In about four billion years, they will merge to form a single, massive galaxy."
    vibe = "Cosmic Drama"
    response_subject = "Galaxies"
    tags = "Milky Way, Andromeda Galaxy, collision, merge, galaxy"
else:
    text, vibe, response_subject, tags = request_chatgpt_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        vibe_needed=True,
        subject_needed=True,
        tags_needed=True,
        max_tokens=300
    )

    if not text:
        print("No response text received. Exiting.")
        sys.exit(1)

print("ChatGPT Text:", text)
print("Vibe:", vibe)
print("Subject:", response_subject)
print("Tags:", tags)

# ──────────────────────────────────────────────────────────────
# Step 4: Prepare output folders
# ──────────────────────────────────────────────────────────────

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
base_output_dir = fr"{config.base_dir}\Clips\{timestamp}"
resources_dir = os.path.join(base_output_dir, "resources")
os.makedirs(resources_dir, exist_ok=True)

log_file_path = os.path.join(base_output_dir, f"{timestamp}.log")
log_file = open(log_file_path, "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

# ──────────────────────────────────────────────────────────────
# Step 5: Choose background music
# ──────────────────────────────────────────────────────────────

directory = config.background_music_dir
mp3_files = [f for f in os.listdir(directory) if f.lower().endswith('.mp3')]

if not mp3_files:
    raise FileNotFoundError("No MP3 files found in the Inspirational folder.")

background_music =  os.path.join(directory, random.choice(mp3_files))

# ──────────────────────────────────────────────────────────────
# Step 6: Download media from Pexels using tags
# ──────────────────────────────────────────────────────────────

# Ensure tags is a list
if isinstance(tags, str):
    tags = [tag.strip() for tag in tags.split(",")]

media_paths = []

for tag in tags:
    print(f"Downloading media for tag: {tag}")
    try:
        tag_output_dir = os.path.join(resources_dir, tag)
        media_count = random.randint(1, 1)
        download_pexels_media(subject=tag, media_count=media_count, output_dir=tag_output_dir)


        if os.path.exists(tag_output_dir):
            for file in os.listdir(tag_output_dir):
                if file.endswith(".mp4"):
                    media_paths.append(os.path.join(tag_output_dir, file))
    except Exception as e:
        print(f"Failed to download media for tag '{tag}': {e}")

# ──────────────────────────────────────────────────────────────
# Step 7: Build arguments for matrix_v1.py
# ──────────────────────────────────────────────────────────────

matrix_script_path = config.matrix_script_path

matrix_args = [
    "python", matrix_script_path,
    "--text", text,
    "--output_path", os.path.join(base_output_dir, f"{timestamp}.mp4"),
    "--fore_color", "0,0,0",
    "--text_remover_style", "fadeout",
    "--typing_sounds_dir", config.typinng_sounds_dir,
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
    "--outro_mp4_path", config.outro_logo_path,
    "--pause_time", "1.2",
    "--gap_pause", "0.5",
    "--gap_pause_last_segment", "3.0"
]

# Add media_paths to matrix_args if any were found
if media_paths:
    matrix_args.extend(["--media_paths"])
    matrix_args.extend(media_paths)

print(matrix_args)

print("Running matrix_v1.py to generate the video...")
subprocess.run(matrix_args)

log_file.close()
