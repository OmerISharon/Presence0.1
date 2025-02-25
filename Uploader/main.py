import os
import sys
import subprocess
import datetime
import shutil
from config import *  # Ensure this provides ROOT_DIR, LOGS_DIR, CHANNELS_ROOT_DIR, etc.

# -----------------------------------------
# Updated Logger Class for Dual Output with Unicode Handling
# -----------------------------------------
class Logger(object):
    """
    A logger class that writes messages to both the terminal and a log file.
    It ensures Unicode is handled gracefully by using UTF-8 with error replacement.
    """
    def __init__(self, filename):
        self.terminal = sys.__stdout__  # original stdout
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

# --------------------------------------
# Function: select_channel()
# --------------------------------------
def select_channel(channels_root):
    """
    Lists available channel folders inside channels_root, and
    allows the user to select one by number or by entering a name manually.
    Returns the selected channel name.
    """
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

# --------------------------------------
# Function: run_script()
# --------------------------------------
def run_script(script_path, channel_name, clip_folder, description):
    """
    Runs the given uploader script using the current Python interpreter,
    passing channel_name and clip_folder as command-line arguments.
    This ensures that in the external uploader script, sys.argv[1] will be
    the channel name and sys.argv[2] will be the clip folder.
    Captures and logs the output of the subprocess.
    """
    print(f"\nINFO: {description} for channel: '{channel_name}', folder: '{clip_folder}'")
    try:
        result = subprocess.run(
            [sys.executable, script_path, channel_name, clip_folder],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: '{os.path.basename(script_path)}' failed with exit code {e.returncode}")
        print(e.output)
        sys.exit(e.returncode)
    print(f"✅ {description} completed successfully.\n")

# --------------------------------------
# Main Function: Auto-Upload Process
# --------------------------------------
def main():
    # Set PYTHONIOENCODING to UTF-8 (best set before the interpreter starts)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.__stdout__.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    # Create a unique log file name based on current timestamp.
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_filename = os.path.join(LOGS_DIR, f"{timestamp_str}.log")
    
    # Redirect stdout and stderr to our Logger instance.
    sys.stdout = Logger(log_filename)
    sys.stderr = sys.stdout

    print(f"INFO: Log file created: {log_filename}\n")
    
    # Determine channel name.
    if len(sys.argv) > 1 and sys.argv[1].strip():
        channel_name = sys.argv[1].strip()
        print(f"\nINFO: Channel provided from command line: {channel_name}")
    else:
        channel_name = select_channel(CHANNELS_ROOT_DIR)
        print(f"\nINFO: Channel selected: {channel_name}")

    # Base directories (adjust as needed)
    base_dir = CHANNELS_ROOT_DIR
    clips_dir = os.path.join(base_dir, channel_name, "Clips")
    metadata_file = os.path.join(base_dir, channel_name, "MetaData", "media_list.txt")
    archive_dir = os.path.join(base_dir, channel_name, "Clips_Archive")

    # Ensure the Clips directory exists.
    if not os.path.isdir(clips_dir):
        print(f"ERROR: Clips directory not found: {clips_dir}")
        sys.exit(1)

    # Get a list of subdirectories (folders) in Clips.
    folders = [os.path.join(clips_dir, d) for d in os.listdir(clips_dir)
               if os.path.isdir(os.path.join(clips_dir, d))]
    if not folders:
        print(f"ERROR: No folders found in: {clips_dir}")
        sys.exit(1)

    # Select the folder with the earliest creation time.
    earliest_folder = min(folders, key=lambda d: os.path.getctime(d))
    print(f"INFO: Earliest folder found: {earliest_folder}")

    # Read the media list from the metadata file.
    if not os.path.exists(metadata_file):
        print(f"ERROR: Media list file not found: {metadata_file}")
        sys.exit(1)

    with open(metadata_file, "r", encoding="utf-8") as f:
        media_list = [line.strip().lower() for line in f if line.strip()]

    # Process each media option.
    for media in media_list:
        if media == "youtube":
            uploader_script = UPLOADER_SCRIPT_YOUTUBE
            description_text = "YouTube AutoUpload"
        elif media == "tiktok":
            uploader_script = UPLOADER_SCRIPT_TIKTOK
            description_text = "TikTok AutoUpload"
        else:
            print(f"WARNING: Unknown media '{media}', skipping.")
            continue

        # Run the uploader script with the channel name and clip folder as arguments.
        run_script(uploader_script, channel_name, earliest_folder, description_text)

    # After all uploads have finished, move the processed folder to the archive directory.
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    
    destination = os.path.join(archive_dir, os.path.basename(earliest_folder))
    print(f"INFO: Moving folder '{earliest_folder}' to archive: {destination}")
    shutil.move(earliest_folder, destination)
    print("INFO: Process completed successfully.")

if __name__ == "__main__":
    main()
