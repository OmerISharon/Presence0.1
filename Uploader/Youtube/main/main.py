import os
import sys
import subprocess
import time
import datetime
from config import *

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
        # List only directories inside the channels_root
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

    # Check if input is a number that corresponds to one of the channels
    if user_input.isdigit():
        index = int(user_input) - 1
        if 0 <= index < len(channels):
            return channels[index]
        else:
            print("ERROR: Invalid channel number selected.")
            sys.exit(1)
    else:
        # If the user types a name, use that.
        return user_input

# --------------------------------------
# Function: run_script()
# --------------------------------------
def run_script(script_path, channel_name, description):
    """
    Runs the given script using the current Python interpreter,
    passing channel_name as an argument.
    Captures and logs the output of the subprocess.
    """
    print(f"\nINFO: {description} for channel: '{channel_name}'")
    try:
        result = subprocess.run(
            [sys.executable, script_path, channel_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        # Print the subprocess output (it will be logged via our Logger)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: '{os.path.basename(script_path)}' failed with exit code {e.returncode}")
        print(e.output)
        sys.exit(e.returncode)
    print(f"✅ {description} completed successfully.\n")

# --------------------------------------
# Main Function
# --------------------------------------
def main():
    # Set PYTHONIOENCODING to UTF-8 (best set before the interpreter starts, but we try here)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    
    # Attempt to reconfigure the original stdout to use UTF-8 with error replacement.
    try:
        sys.__stdout__.reconfigure(encoding="utf-8", errors="replace")
    except Exception as e:
        # If reconfigure is not available, we continue.
        pass

    # Create a unique log file name based on current timestamp.
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_filename = os.path.join(LOGS_DIR, f"{timestamp}.log")
    
    # Redirect stdout and stderr to our Logger instance.
    sys.stdout = Logger(log_filename)
    sys.stderr = sys.stdout

    print(f"INFO: Log file created: {log_filename}\n")
    
    # Check if a channel name was passed as a command-line parameter.
    if len(sys.argv) > 1 and sys.argv[1].strip():
        channel_name = sys.argv[1].strip()
        print(f"\nINFO: Channel provided from command line: {channel_name}")
    else:
        # If no parameter is passed, prompt the user.
        channel_name = select_channel(CHANNELS_ROOT_DIR)
        print(f"\nINFO: Channel selected: {channel_name}")

    # Save the paths of the two scripts as variables.
    switch_account_script = os.path.join(ROOT_DIR, "SwitchAccount - Youtube", "Code", "SwitchAccount - Youtube.py")
    auto_upload_script    = os.path.join(ROOT_DIR, "AutoUpload - Youtube", "Code", "AutoUploadYouTube.py")

    # Run the Switch Account script.
    run_script(switch_account_script, channel_name, "SwitchAccount")

    time.sleep(3)

    # After SwitchAccount finishes, run the AutoUpload script.
    run_script(auto_upload_script, channel_name, "AutoUpload")

    print("INFO: All operations have completed successfully!")

if __name__ == "__main__":
    main()
