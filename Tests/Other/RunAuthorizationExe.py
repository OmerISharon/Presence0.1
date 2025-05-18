import json
import subprocess
import os

# Define the path to the JSON file.
json_file = "C:\\Users\\omers\\AppData\\Roaming\\POC-Platform-Engagement-Poller\\AuthorizationRefreshNotifications.json"

# Ensure the file exists before loading.
if not os.path.exists(json_file):
    raise FileNotFoundError(f"JSON file {json_file} not found.")

# Load JSON content.
with open(json_file, 'r') as f:
    data = json.load(f)

# Process each command in the JSON list.
for item in data:
    exec_command = item.get("ExecutableCommand")
    if not exec_command:
        print("No ExecutableCommand found; skipping entry.")
        continue

    print("Executing command:")
    print(exec_command)

    # Option 1: Using shell=True so that the command string is interpreted by CMD.
    try:
        process = subprocess.Popen(exec_command, shell=True)
        # Optionally wait for the process to complete:
        process.wait()
        print("Command executed successfully.")
    except Exception as e:
        print(f"Failed to execute command: {e}")