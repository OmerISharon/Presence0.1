import os
import sys
import subprocess
import time
from config import *

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
        print(f"❌ ERROR: Unable to read channels directory '{channels_root}': {e}")
        sys.exit(1)

    if channels:
        print("\n📂 Available Channels:")
        for idx, channel in enumerate(channels, start=1):
            print(f"  {idx}. {channel}")
    else:
        print("⚠️  No existing channels found.")

    user_input = input("\n👉 Enter a channel name or number (or type a new channel name): ").strip()

    # Check if input is a number that corresponds to one of the channels
    if user_input.isdigit():
        index = int(user_input) - 1
        if 0 <= index < len(channels):
            return channels[index]
        else:
            print("❌ ERROR: Invalid channel number selected.")
            sys.exit(1)
    else:
        # If the user types a name, use that.
        return user_input

def run_script(script_path, channel_name, description):
    """
    Runs the given script using the current Python interpreter,
    passing channel_name as an argument.
    """
    print(f"\n🔄 {description} for channel: '{channel_name}'")
    try:
        subprocess.run([sys.executable, script_path, channel_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: '{os.path.basename(script_path)}' failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    print(f"✅ {description} completed successfully.\n")

def main():
    # Prompt user to choose a channel.
    channel_name = select_channel(CHANNELS_ROOT_DIR)
    print(f"\n👉 Channel selected: {channel_name}")

    # Save the paths of the two scripts as variables.
    switch_account_script = f"{ROOT_DIR}\\SwitchAccount - Youtube\\Code\\SwitchAccount - Youtube.py"
    auto_upload_script    = f"{ROOT_DIR}\\AutoUpload - Youtube\\Code\\AutoUploadYouTube.py"

    # Run the Switch Account script.
    run_script(switch_account_script, channel_name, "SwitchAccount")

    time.sleep(3)

    # After SwitchAccount finishes, run the AutoUpload script.
    run_script(auto_upload_script, channel_name, "AutoUpload")

    print("🎉 All operations have completed successfully!")

if __name__ == "__main__":
    main()
