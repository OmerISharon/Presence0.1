import os
import sys
import subprocess
import datetime
import shutil
import json
from config import *  # Ensure this provides ROOT_DIR, LOGS_DIR, CHANNELS_ROOT_DIR, etc.

INTERNAL_MODULES_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Internal_Modules"
sys.path.insert(0, INTERNAL_MODULES_DIR)
import utilities.keyboard_switcher.keyboard_switcher as keyboard_switcher

UPLOAD_LOG_PATH = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Uploader\\Logs\\global_uploader_logs.json"

class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.__stdout__
        self.log = open(filename, "a", encoding="utf-8", errors="replace")
    def write(self, message):
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode('utf-8', errors='replace').decode('utf-8'))
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

def select_channel(channels_root):
    try:
        channels = [d for d in os.listdir(channels_root) if os.path.isdir(os.path.join(channels_root, d))]
    except Exception as e:
        print(f"ERROR: Unable to read channels directory '{channels_root}': {e}")
        sys.exit(1)

    if channels:
        print("\nINPUT: Available Channels:")
        for idx, channel in enumerate(channels, start=1):
            print(f"  {idx}. {channel}")
    else:
        print("ERROR: No existing channels found.")

    user_input = input("\nINPUT: Enter a channel name or number (or type a new channel name): ").strip()

    if user_input.isdigit():
        index = int(user_input) - 1
        if 0 <= index < len(channels):
            return channels[index]
        else:
            print("ERROR: Invalid channel number selected.")
            sys.exit(1)
    else:
        return user_input

def update_upload_log(channel_name, platform, status, log_path, exception=None):
    os.makedirs(os.path.dirname(UPLOAD_LOG_PATH), exist_ok=True)
    try:
        if os.path.exists(UPLOAD_LOG_PATH):
            with open(UPLOAD_LOG_PATH, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = {}

        if channel_name not in logs:
            logs[channel_name] = {}

        logs[channel_name][platform] = {
            "last_uploaded": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "exception": exception or "",
            "log_file": log_path
        }

        with open(UPLOAD_LOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4)

    except Exception as e:
        print(f"ERROR: Failed to update upload log: {e}")

def run_script(script_path, channel_name, clip_folder, platform, log_path):
    print(f"\nACTION: Running {platform.title()} Uploader\nCHANNEL: '{channel_name}',\nINPUT: '{clip_folder}'")
    try:
        result = subprocess.run(
            [sys.executable, script_path, channel_name, clip_folder],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print(result.stdout)
        update_upload_log(channel_name, platform, status="success", log_path=log_path)
        print(f"✅ {platform.title()} upload completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: '{os.path.basename(script_path)}' failed with exit code {e.returncode}")
        print(e.output)
        update_upload_log(channel_name, platform, status="failure", log_path=log_path, exception=e.output)
        sys.exit(e.returncode)

def main():
    keyboard_switcher.switch_to_english()

    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.__stdout__.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_filename = os.path.join(LOGS_DIR, f"{timestamp_str}.log")
    sys.stdout = Logger(log_filename)
    sys.stderr = sys.stdout

    print(f"INFO: Log file created: {log_filename}\n")

    if len(sys.argv) > 1 and sys.argv[1].strip():
        channel_name = sys.argv[1].strip()
        print(f"\nINFO: Channel provided from command line: {channel_name}")
    else:
        channel_name = select_channel(CHANNELS_ROOT_DIR)
        print(f"\nINFO: Channel selected: {channel_name}")

    base_dir = CHANNELS_ROOT_DIR
    clips_dir = os.path.join(base_dir, channel_name, "Clips")
    metadata_file = os.path.join(base_dir, channel_name, "MetaData", "media_list.txt")
    archive_dir = os.path.join(base_dir, channel_name, "Clips_Archive")

    if not os.path.isdir(clips_dir):
        print(f"ERROR: Clips directory not found: {clips_dir}")
        sys.exit(1)

    folders = [os.path.join(clips_dir, d) for d in os.listdir(clips_dir) if os.path.isdir(os.path.join(clips_dir, d))]
    if not folders:
        print(f"ERROR: No folders found in: {clips_dir}")
        sys.exit(1)

    earliest_folder = min(folders, key=lambda d: os.path.getctime(d))
    print(f"INFO: Earliest folder found: {earliest_folder}")

    if not os.path.exists(metadata_file):
        print(f"ERROR: Media list file not found: {metadata_file}")
        sys.exit(1)

    with open(metadata_file, "r", encoding="utf-8") as f:
        media_list = [line.strip().lower() for line in f if line.strip()]

    for media in media_list:
        if media == "youtube":
            run_script(UPLOADER_SCRIPT_YOUTUBE, channel_name, earliest_folder, "youtube", log_filename)
        elif media == "tiktok":
            run_script(UPLOADER_SCRIPT_TIKTOK, channel_name, earliest_folder, "tiktok", log_filename)
        elif media == "instagram":
            run_script(UPLOADER_SCRIPT_INSTAGRAM, channel_name, earliest_folder, "instagram", log_filename)
        else:
            print(f"WARNING: Unknown media '{media}', skipping.")

    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    destination = os.path.join(archive_dir, os.path.basename(earliest_folder))
    print(f"INFO: Moving folder '{earliest_folder}' to archive: {destination}")
    shutil.move(earliest_folder, destination)
    print("INFO: Process completed successfully.")

if __name__ == "__main__":
    main()
