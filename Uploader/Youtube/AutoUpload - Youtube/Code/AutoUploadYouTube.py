import os
import sys
import time
import json
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import *
sys.path.insert(0, RESOURCES_DIR)
from chrome_config import *

# -----------------------------------------------------------------------------
# 1. Get channel name from command-line argument and build directory paths.
# -----------------------------------------------------------------------------
if len(sys.argv) < 2:
    print("ERROR: Please provide the CHANNEL_NAME as a command-line argument.")
    sys.exit(1)

CHANNEL_NAME = sys.argv[1]
INPUT_DIR = f"{CHANNELS_ROOT_DIR}\\{CHANNEL_NAME}\\Clips"
ARCHIVE_DIR = f"{CHANNELS_ROOT_DIR}\\{CHANNEL_NAME}\\Clips_Archive"

# -----------------------------------------------------------------------------
# 2. Configure Chrome options.
# -----------------------------------------------------------------------------
options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
options.add_argument(f"user-data-dir={CHROME_BETA_USER_DATA_DIR}")
options.binary_location = CHROME_BETA_EXE_PATH

def start_browser():
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
# 3. Get the earliest folder (by creation time) and select the MP4 file from it.
# -----------------------------------------------------------------------------
def get_earliest_video():
    try:
        # List all folders in INPUT_DIR.
        folders = [f for f in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, f))]
    except Exception as e:
        print(f"ERROR: Could not list directory {INPUT_DIR}: {e}")
        sys.exit(1)
    
    if not folders:
        print(f"ERROR: No folders found in {INPUT_DIR}")
        sys.exit(1)
    
    # Select the folder with the earliest creation time.
    earliest_folder = min(folders, key=lambda f: os.path.getctime(os.path.join(INPUT_DIR, f)))
    folder_path = os.path.join(INPUT_DIR, earliest_folder)
    
    # Inside the folder, find MP4 file(s).
    mp4_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]
    if not mp4_files:
        print(f"ERROR: No MP4 files found in folder {folder_path}")
        sys.exit(1)
    
    # If more than one, select the MP4 file with the earliest creation time.
    mp4_file = min(mp4_files, key=lambda f: os.path.getctime(os.path.join(folder_path, f)))
    video_path = os.path.join(folder_path, mp4_file)
    
    # Get the creation time of the folder and format it as a timestamp.
    creation_time = os.path.getctime(folder_path)
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(creation_time))
    
    return folder_path, video_path, timestamp

# -----------------------------------------------------------------------------
# 4. Update title and description using the JSON file found in the folder.
# -----------------------------------------------------------------------------
def update_video_details(bot, folder_path):
    # Find the JSON file inside the folder.
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    if not json_files:
        print(f"ERROR: No JSON file found in folder {folder_path}")
        return
    
    # Choose the first JSON file (adjust if needed for your structure).
    json_file = json_files[0]
    json_path = os.path.join(folder_path, json_file)
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    new_title = data.get("title", "")
    new_description = data.get("description", "")

    print("INFO: Updating video title and description...")

    try:
        # Wait until both text boxes (for title and description) are present.
        text_boxes = WebDriverWait(bot, 60).until(
            EC.presence_of_all_elements_located((By.ID, "textbox"))
        )
        if len(text_boxes) < 2:
            print("ERROR: Could not locate both title and description text boxes.")
            return
        
        # Update Title (assumed to be the first textbox)
        title_box = text_boxes[0]
        title_box.click()
        time.sleep(1)
        title_box.clear()
        time.sleep(1)
        title_box.send_keys(new_title)
        time.sleep(1)

        # Update Description (assumed to be the second textbox)
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

    # Update the video details using the JSON file from the folder.
    update_video_details(bot, folder_path)

    # Proceed by clicking "Next" three times.
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
    # Ensure the input directory exists.
    if not os.path.exists(INPUT_DIR):
        print(f"ERROR: Input directory not found: {INPUT_DIR}")
        sys.exit(1)

    # Get the earliest folder containing the video and JSON file.
    folder_path, video_path, timestamp = get_earliest_video()
    print(f"INFO: Selected folder: {folder_path}")
    print(f"INFO: Video file: {video_path} (Timestamp: {timestamp})")

    bot = start_browser()
    try:
        upload_video(bot, video_path, folder_path, timestamp)
    finally:
        bot.quit()

    # After a successful upload, move the entire folder to the archive directory.
    try:
        if not os.path.exists(ARCHIVE_DIR):
            os.makedirs(ARCHIVE_DIR)
        archive_path = os.path.join(ARCHIVE_DIR, os.path.basename(folder_path))
        shutil.move(folder_path, archive_path)
        print(f"INFO: Folder moved to archive: {archive_path}")
    except Exception as e:
        print(f"ERROR: Failed to move folder to archive: {e}")

    print("INFO: Auto-upload process completed successfully.")

if __name__ == "__main__":
    main()
