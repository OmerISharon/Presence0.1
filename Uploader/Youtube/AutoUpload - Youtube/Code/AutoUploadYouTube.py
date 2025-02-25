import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import *
sys.path.insert(0, RESOURCES_DIR)
from chrome_config import *

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
# 1. Get channel name and folder path from command-line arguments.
# -----------------------------------------------------------------------------
if len(sys.argv) < 3:
    print("ERROR: Please provide the CHANNEL_NAME and CLIP_FOLDER_PATH as command-line arguments.")
    sys.exit(1)

CHANNEL_NAME = sys.argv[1]
folder_path = sys.argv[2]  # The directory containing the clip to upload

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

    service = Service(CHROME_BETA_DRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def wait_for_element(bot, by, identifier, timeout=120):
    return WebDriverWait(bot, timeout).until(EC.element_to_be_clickable((by, identifier)))

def close_popups(bot):
    try:
        popups = bot.find_elements(By.XPATH, '//ytcp-button[contains(@aria-label, "Close")]')
        for popup in popups:
            popup.click()
            time.sleep(1)
    except Exception as e:
        print(f"Warning: Could not close pop-ups. {e}")

# -----------------------------------------------------------------------------
# 3. From the provided folder, extract the latest MP4 file and its timestamp.
# -----------------------------------------------------------------------------
def get_latest_video(folder_path):
    # Filter MP4 files and ignore those that contain "tmp" (case-insensitive)
    mp4_files = [
        f for f in os.listdir(folder_path)
        if f.endswith(".mp4") and "tmp" not in f.lower()
    ]
    if not mp4_files:
        print(f"ERROR: No MP4 files found in folder {folder_path}")
        sys.exit(1)
    
    # Select the MP4 file with the latest creation time.
    mp4_file = max(mp4_files, key=lambda f: os.path.getctime(os.path.join(folder_path, f)))
    video_path = os.path.join(folder_path, mp4_file)
    
    # Use the folder's creation time as a timestamp.
    creation_time = os.path.getctime(folder_path)
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(creation_time))
    
    return video_path, timestamp


# -----------------------------------------------------------------------------
# 4. Update title and description using the JSON file found in the folder.
# -----------------------------------------------------------------------------
def update_video_details(bot, folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    if not json_files:
        print(f"ERROR: No JSON file found in folder {folder_path}")
        return
    
    json_file = json_files[0]
    json_path = os.path.join(folder_path, json_file)
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    new_title = data.get("title", "")
    new_description = data.get("description", "")

    print("INFO: Updating video title and description...")

    try:
        text_boxes = WebDriverWait(bot, 60).until(
            EC.presence_of_all_elements_located((By.ID, "textbox"))
        )
        if len(text_boxes) < 2:
            print("ERROR: Could not locate both title and description text boxes.")
            return
        
        # Update Title (first textbox)
        title_box = text_boxes[0]
        title_box.click()
        time.sleep(1)
        title_box.clear()
        time.sleep(1)
        title_box.send_keys(new_title)
        time.sleep(1)

        # Update Description (second textbox)
        description_box = text_boxes[1]
        description_box.click()
        time.sleep(1)
        description_box.clear()
        time.sleep(1)
        description_box.send_keys(new_description)
        time.sleep(1)

        print("INFO: Video details updated successfully.")
    except Exception as e:
        print(f"ERROR: Failed to update video details: {e}")

# -----------------------------------------------------------------------------
# 5. Upload video using Selenium.
# -----------------------------------------------------------------------------
def upload_video(bot, video_path, folder_path, timestamp):
    print(f"INFO: Initiating upload for video: {video_path}")
    
    bot.get("https://studio.youtube.com")
    
    WebDriverWait(bot, 60).until(EC.presence_of_element_located((By.ID, "upload-icon")))
    upload_button = wait_for_element(bot, By.ID, "upload-icon")
    upload_button.click()
    time.sleep(3)

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
    time.sleep(10)

    close_popups(bot)
    print("INFO: Waiting for YouTube to finish processing the video...")

    processing_done = False
    wait_time = 0
    while wait_time < 600:
        try:
            next_button = bot.find_element(By.ID, "next-button")
            if next_button.is_enabled():
                print("INFO: Video processing completed.")
                processing_done = True
                break
        except Exception:
            pass

        time.sleep(10)
        wait_time += 10

        if wait_time % 120 == 0:
            print("INFO: Refreshing page to check processing status...")
            bot.refresh()
            time.sleep(5)

    if not processing_done:
        print("ERROR: Video processing exceeded time limit. Aborting upload.")
        bot.quit()
        return

    update_video_details(bot, folder_path)

    # Click "Next" three times.
    for i in range(3):
        retry_count = 0
        while retry_count < 3:
            try:
                next_button = WebDriverWait(bot, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//ytcp-button[contains(@id, "next-button")]'))
                )
                bot.execute_script("arguments[0].scrollIntoView();", next_button)
                time.sleep(1)
                bot.execute_script("arguments[0].click();", next_button)
                print(f"INFO: Clicked 'Next' button ({i+1}/3).")
                break
            except Exception as e:
                print(f"Warning: 'Next' button not clickable, retrying... ({retry_count + 1}/3). Error: {e}")
                bot.refresh()
                time.sleep(5)
                retry_count += 1

    # Click "Done" to finalize the upload.
    try:
        done_button = WebDriverWait(bot, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//ytcp-button[contains(@id, "done-button")]'))
        )
        bot.execute_script("arguments[0].scrollIntoView();", done_button)
        time.sleep(1)
        bot.execute_script("arguments[0].click();", done_button)
        print("INFO: 'Done' button clicked. Video upload finalized.")
    except Exception as e:
        print(f"ERROR: Unable to click 'Done' button: {e}")
    
    time.sleep(5)

# -----------------------------------------------------------------------------
# Main routine
# -----------------------------------------------------------------------------
def main():
    if not os.path.exists(folder_path):
        print(f"ERROR: Provided folder not found: {folder_path}")
        sys.exit(1)

    video_path, timestamp = get_latest_video(folder_path)
    print(f"INFO: Video file: {video_path} (Timestamp: {timestamp})")

    bot = start_browser()
    try:
        upload_video(bot, video_path, folder_path, timestamp)
    finally:
        bot.quit()

    print("INFO: YouTube upload process completed successfully.")

if __name__ == "__main__":
    main()
