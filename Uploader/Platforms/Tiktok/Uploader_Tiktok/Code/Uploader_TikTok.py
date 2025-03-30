import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from config import *
sys.path.insert(0, RESOURCES_DIR)
from chrome_config import *
sys.path.insert(0, INTERNAL_MODULES_DIR)

# First, set keyboard layout to English - before any other operations
try:
    from keyboard_switcher import keyboard
    print("INFO: Setting keyboard layout to English...")
    if keyboard.set_english():
        print("INFO: Keyboard layout successfully set to English.")
    else:
        print("WARNING: Failed to set keyboard layout to English. Continuing anyway...")
except Exception as e:
    print(f"WARNING: Could not set keyboard to English: {e}")

# -----------------------------------------------------------------------------
# Function to map the display profile name (e.g. "God Mode Notes") to the actual
# Chrome profile folder (e.g. "Profile 1" or "Default") using the Local State file.
# -----------------------------------------------------------------------------
def get_profile_directory(profile_name):
    local_state_path = os.path.join(CHROME_BETA_USER_DATA_DIR, "Local State")
    if not os.path.exists(local_state_path):
        print("ERROR: Chrome Local State file not found. Cannot determine profiles.")
        return None
    with open(local_state_path, "r", encoding="utf-8") as file:
        local_state = json.load(file)
    profiles = local_state.get("profile", {}).get("info_cache", {})
    for profile_folder, details in profiles.items():
        if details.get("name") == profile_name:
            return profile_folder  # e.g., "Profile 1" or "Default"
    print(f"ERROR: Profile '{profile_name}' not found.")
    return None

# -----------------------------------------------------------------------------
# 1. Get channel name and clip folder path from command-line arguments.
# -----------------------------------------------------------------------------
if len(sys.argv) < 3:
    print("ERROR: Please provide the CHANNEL_NAME and CLIP_FOLDER_PATH as command-line arguments.")
    sys.exit(1)

CHANNEL_NAME = sys.argv[1]
folder_path = sys.argv[2]  # Directory containing the clip to upload

# -----------------------------------------------------------------------------
# 2. Configure Chrome options using the mapped profile folder.
# -----------------------------------------------------------------------------
def start_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument(f"--user-data-dir={CHROME_BETA_USER_DATA_DIR}")
    
    profile_folder = get_profile_directory(CHANNEL_NAME)
    if not profile_folder:
        sys.exit(1)
    options.add_argument(f"--profile-directory={profile_folder}")
    options.binary_location = CHROME_BETA_EXE_PATH

    # Let Selenium Manager automatically handle the driver selection.
    return webdriver.Chrome(options=options)

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def wait_for_element(bot, by, identifier, timeout=120):
    return WebDriverWait(bot, timeout).until(EC.element_to_be_clickable((by, identifier)))

def close_popups(bot):
    try:
        popups = bot.find_elements(By.XPATH, '//*[contains(@aria-label, "Close")]')
        for popup in popups:
            popup.click()
            time.sleep(0.5)
    except Exception as e:
        print(f"Warning: Could not close pop-ups. {e}")

# -----------------------------------------------------------------------------
# 3. From the provided folder, extract the latest MP4 file and its timestamp.
# -----------------------------------------------------------------------------
def get_latest_video(folder_path):
    # Filter MP4 files and ignore those that contain "tmp" (case-insensitive)
    mp4_files = [f for f in os.listdir(folder_path)
                 if f.endswith(".mp4") and "tmp" not in f.lower()]
    if not mp4_files:
        print(f"ERROR: No MP4 files found in folder {folder_path}")
        sys.exit(1)
    # Select the MP4 file with the latest creation time.
    mp4_file = max(mp4_files, key=lambda f: os.path.getctime(os.path.join(folder_path, f)))
    video_path = os.path.join(folder_path, mp4_file)
    creation_time = os.path.getctime(folder_path)
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(creation_time))
    return video_path, timestamp


# -----------------------------------------------------------------------------
# 4. Read the first JSON file in the folder to extract the description.
# -----------------------------------------------------------------------------
def get_video_description(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    if not json_files:
        print(f"ERROR: No JSON file found in folder {folder_path}")
        return ""
    json_file = json_files[0]
    json_path = os.path.join(folder_path, json_file)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("description", "")

# -----------------------------------------------------------------------------
# 5. Upload video to TikTok using Selenium.
# -----------------------------------------------------------------------------
def upload_video(bot, video_path, folder_path, timestamp, description):
    print(f"INFO: Initiating TikTok upload for video: {video_path}")
    
    # Navigate to TikTok upload page (ensure you are logged in via the chosen profile)
    bot.get("https://www.tiktok.com/upload")
    
    # Wait for the file input element to be present.
    file_input = WebDriverWait(bot, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    
    abs_path = os.path.abspath(video_path)
    if not os.path.exists(abs_path):
        print(f"ERROR: Video file not found -> {abs_path}")
        bot.quit()
        return
    
    file_input.send_keys(abs_path)
    print("INFO: Video file selected for upload.")
    time.sleep(5)  # Reduced wait time for processing/upload
    
    # Close any popups that may appear.
    close_popups(bot)
    
    # Determine expected placeholder text from the video file name (without extension).
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    print(f"INFO: Expected placeholder (current text) in description editor: '{video_name}'")
    
    # Locate the description editor by finding a div that is contenteditable and contains the video_name.
    try:
        description_area = WebDriverWait(bot, 60).until(
            EC.presence_of_element_located((
                By.XPATH, 
                f"//div[@contenteditable='true' and contains(@class, 'public-DraftEditor-content') and .//span[text()='{video_name}']]"
            ))
        )
        print("INFO: Found description editor using placeholder match.")
    except Exception as e:
        print("WARNING: Could not locate description editor by placeholder; falling back to generic contenteditable locator.")
        description_area = WebDriverWait(bot, 60).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true' and contains(@class, 'public-DraftEditor-content')]"))
        )
    
    # Clear the editor by both JavaScript and sending multiple BACKSPACE keystrokes.
    try:
        # Clear using JavaScript first.
        bot.execute_script("arguments[0].innerHTML = '';", description_area)
        time.sleep(0.5)
        # Click the editor.
        description_area.click()
        time.sleep(0.5)
        # Optionally, send CTRL+A then BACKSPACE.
        description_area.send_keys(Keys.CONTROL, "a")
        time.sleep(0.5)
        description_area.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)
        # Send 50 BACKSPACE keystrokes to ensure clearing.
        for _ in range(50):
            description_area.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)
        # Now send the metadata description.
        description_area.send_keys(description)
        print("INFO: Description updated with metadata.")
    except Exception as e:
        print(f"ERROR: Could not update description: {e}")
    
    # Scroll down to ensure the Post button is visible and click it.
    try:
        post_button = WebDriverWait(bot, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Post']"))
        )
        bot.execute_script("arguments[0].scrollIntoView(true);", post_button)
        time.sleep(0.5)
        post_button.click()
        print("INFO: 'Post' button clicked. TikTok upload finalized.")
    except Exception as e:
        print(f"ERROR: Unable to click 'Post' button: {e}")
    
    time.sleep(3)

# -----------------------------------------------------------------------------
# Main routine
# -----------------------------------------------------------------------------
def main():
    if not os.path.exists(folder_path):
        print(f"ERROR: Provided folder not found: {folder_path}")
        sys.exit(1)

    video_path, timestamp = get_latest_video(folder_path)
    description = get_video_description(folder_path)
    print(f"INFO: Video file: {video_path} (Timestamp: {timestamp})")
    print(f"INFO: Description: {description}")

    bot = start_browser()
    try:
        upload_video(bot, video_path, folder_path, timestamp, description)
    finally:
        bot.quit()

    print("INFO: TikTok upload process completed successfully.")

if __name__ == "__main__":
    main()
