import os
import shutil

# List of files to copy
files_to_copy = [
    "p232.wav",
    "p236.wav",
    "p239.wav",
    "p251.wav",
    "p254.wav",
    "p265.wav",
    "p267.wav",
    "p286.wav",
    "p287.wav",
    "p302.wav",
    "p307.wav",
    "p317.wav"
]

# Source and destination directories
dir_a = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Creator\\The Science Of Getting Rich\\Tests\\TTS\\Output_Dir"
dir_b = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Creator\\The Science Of Getting Rich\\Tests\\TTS\\Favorites"

# Ensure destination directory exists
os.makedirs(dir_b, exist_ok=True)

# Copy each file from dir_a to dir_b
for file_name in files_to_copy:
    src = os.path.join(dir_a, file_name)
    dst = os.path.join(dir_b, file_name)
    
    if os.path.exists(src):
        print(f"Copying {src} to {dst}")
        shutil.copy(src, dst)
    else:
        print(f"File {src} does not exist, skipping.")
