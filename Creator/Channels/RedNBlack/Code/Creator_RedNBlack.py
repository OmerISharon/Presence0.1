import os
import re
import subprocess
import datetime
import sys

import config

# Setup project modules path
Modules_Dir = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Internal_Modules"
sys.path.insert(0, Modules_Dir)

from utilities.request_chatgpt.request_chatgpt import request_chatgpt_response
from utilities.string_manager.string_manager import normalize_hebrew

debug_mode = False  # Set to False to enable real ChatGPT API call

# ──────────────────────────────────────────────────────────────
# Step 1: Set prompts for ChatGPT
# ──────────────────────────────────────────────────────────────

system_prompt = (
    "You are a brutal, no-excuses motivator. Your job is to deliver dark, aggressive, and ruthless motivational speeches "
    "that slap the listener awake and fuel raw determination. Speak with authority. Be mean, but with purpose. "
    "Your words should cut deep — no fluff, no fake positivity. Each speech must hit hard using simple, clear language. "
    "Write 3 to 5 short, savage sentences. Each sentence must end with a period (.) to create a powerful, punchy rhythm. "
    "No commas. No run-ons. Just cold truth. The listener should feel angry, fired up, and ready to prove everyone wrong."
)

user_prompt = (
    "Give me a hard-core motivational speech. Make it short, dark, and mean. "
    "Use only simple words that even a 12-year-old can understand. "
    "Write exactly 3 to 5 sentences. End every sentence with a period. No commas, no soft pauses. "
    "Make me feel like I’ve wasted my time and now I have to fight for everything. Fuel my rage."
)

# ──────────────────────────────────────────────────────────────
# Step 2: Get ChatGPT response
# ──────────────────────────────────────────────────────────────

if debug_mode:
    text = "You've been lazy. Time is slipping while you pity yourself. Stand up and grind, or stay nothing."
else:
    text, vibe, response_subject, tags = request_chatgpt_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        vibe_needed=False,
        subject_needed=False,
        tags_needed=False,
        max_tokens=300,
        prompts_history = fr"{config.base_dir}\Clips"
    )

    if not text:
        print("No response text received. Exiting.")
        sys.exit(1)

print("ChatGPT Text:", text)

# ──────────────────────────────────────────────────────────────
# Step 3: Prepare output folders
# ──────────────────────────────────────────────────────────────

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
base_output_dir = fr"{config.base_dir}\Clips\{timestamp}"
os.makedirs(base_output_dir, exist_ok=True)

log_file_path = os.path.join(base_output_dir, f"{timestamp}.log")
log_file = open(log_file_path, "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

# ──────────────────────────────────────────────────────────────
# Step 4: Build arguments for matrix_v1.py
# ──────────────────────────────────────────────────────────────

matrix_script_path = config.matrix_script_path

matrix_args = [
    "python", matrix_script_path,
    "--text", normalize_hebrew(text),
    "--output_path", os.path.join(base_output_dir, f"{timestamp}.mp4"),
    "--fore_color", "255,0,0",
    "--bg_color", "0,0,0",
    "--text_remover_style", "fadeout",
    "--text_appearance_style", "fade",
    "--typing_sounds_dir", config.typinng_sounds_dir,
    "--typing_sounds_volume", "1.5",
    "--font_size", "64",
    "--font_path", fr"C:\Windows\Fonts\AGENCYR.TTF",
    "--separate_by_comma", "False",
    "--pause_time", "1.5",
]

print(matrix_args)

print("Running matrix_v1.py to generate the video...")
subprocess.run(matrix_args)

log_file.close()
