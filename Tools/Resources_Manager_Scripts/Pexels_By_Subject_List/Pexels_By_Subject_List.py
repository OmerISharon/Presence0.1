import os
import subprocess
from subjects import subjects_v1

# Path to the video download script
target_script = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Internal_Modules\\utilities\\get_pexels_media\\get_pexels_media.py"

# Optional final step scripts
resource_tideup_path = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Tools\\Resources_Manager\\Resource_Tideup\\Resource_Tideup.py"
overall_json_creator_path = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Tools\\Resources_Manager\\Generate_Resource_Json_Map\\Generate_Resource_Json_Map.py"

# Flags
run_resource_tideup = True
run_overall_json_creator = True

# Process all subjects
for subject in subjects_v1:
    print(f"\n--- Processing subject: {subject} ---")
    try:
        subprocess.run(["python", target_script, subject], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing subject '{subject}': {e}")

# Run Resource Tideup if enabled
if run_resource_tideup:
    print("\n--- Running Resource_Tideup.py ---")
    try:
        subprocess.run(["python", resource_tideup_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Resource_Tideup: {e}")

# Run JSON Creator if enabled
if run_overall_json_creator:
    print("\n--- Running Generate_Resource_Json_Map.py ---")
    try:
        subprocess.run(["python", overall_json_creator_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Generate_Resource_Json_Map: {e}")
