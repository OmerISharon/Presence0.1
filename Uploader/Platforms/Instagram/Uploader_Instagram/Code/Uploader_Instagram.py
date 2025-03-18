import os
import sys
import json
import time
import threading
import pyautogui
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import *
sys.path.insert(0, RESOURCES_DIR)
from chrome_config import *

def get_profile_directory(profile_name):
    """Map the display profile name to the actual Chrome profile folder."""
    local_state_path = os.path.join(CHROME_BETA_USER_DATA_DIR, "Local State")
    if not os.path.exists(local_state_path):
        print("ERROR: Chrome Local State file not found. Cannot determine profiles.")
        return None
    with open(local_state_path, "r", encoding="utf-8") as file:
        local_state = json.load(file)
    profiles = local_state.get("profile", {}).get("info_cache", {})
    for folder, details in profiles.items():
        if details.get("name") == profile_name:
            return folder
    print(f"ERROR: Profile '{profile_name}' not found in Local State.")
    return None

if len(sys.argv) < 3:
    print("ERROR: Please provide the CHANNEL_NAME and CLIP_FOLDER_PATH as command-line arguments.")
    sys.exit(1)

CHANNEL_NAME = sys.argv[1]
folder_path = sys.argv[2]

def start_browser(channel_name):
    """Configure Chrome in desktop mode with the specified user profile and maximize the window."""
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    profile_folder = get_profile_directory(channel_name)
    if not profile_folder:
        sys.exit(1)
    options.add_argument(f"--user-data-dir={CHROME_BETA_USER_DATA_DIR}")
    options.add_argument(f"--profile-directory={profile_folder}")
    options.binary_location = CHROME_BETA_EXE_PATH
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    time.sleep(1)
    return driver

def wait_clickable(bot, xpath, timeout=30):
    return WebDriverWait(bot, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))

def try_click(bot, element):
    """Try clicking the element via ActionChains, then JS if needed."""
    try:
        ActionChains(bot).move_to_element(element).click().perform()
        return True
    except Exception:
        pass
    try:
        bot.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        bot.execute_script("arguments[0].click();", element)
        return True
    except Exception:
        return False

def check_and_cancel_discard_popup(bot, timeout=5):
    """
    Checks if the 'Discard post?' popup is present.
    If it is, clicks 'Cancel' and returns True.
    Otherwise returns False.
    """
    try:
        # Look for any dialog containing 'Discard post' text
        discard_dialog = WebDriverWait(bot, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@role='dialog']//*[contains(., 'Discard post')]")
            )
        )
        print("INFO: Discard popup detected.")
        # Inside that dialog, find the 'Cancel' button
        cancel_button = discard_dialog.find_element(
            By.XPATH, ".//button[contains(., 'Cancel')]"
        )
        if not try_click(bot, cancel_button):
            print("WARNING: Could not click 'Cancel' in discard popup.")
        else:
            print("INFO: Discard popup canceled.")
        return True
    except Exception:
        return False

def get_latest_video(folder_path):
    """Return the newest MP4 file in the folder."""
    mp4_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4") and "tmp" not in f.lower()]
    if not mp4_files:
        print(f"ERROR: No MP4 files found in {folder_path}")
        sys.exit(1)
    mp4_file = max(mp4_files, key=lambda f: os.path.getctime(os.path.join(folder_path, f)))
    return os.path.join(folder_path, mp4_file)

def get_description_from_json(folder_path):
    """Return the 'description' from the first JSON file in the folder."""
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    if not json_files:
        return ""
    json_path = os.path.join(folder_path, json_files[0])
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("description", "")

def paste_description_into_caption(bot, folder_path):
    description_text = get_description_from_json(folder_path)
    if not description_text:
        print("INFO: No 'description' in JSON. Skipping caption update.")
        return
    print(f"INFO: Pasting description into caption: {description_text}")
    try:
        caption_field = WebDriverWait(bot, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@aria-label='Write a caption...' and @role='textbox']")
            )
        )
        if not try_click(bot, caption_field):
            print("ERROR: Cannot focus the caption field.")
            return
        time.sleep(1)
        ActionChains(bot).send_keys(description_text).perform()
        print("INFO: Description pasted successfully.")
    except Exception as e:
        print(f"ERROR: Failed to paste description: {e}")

def click_next_crop(bot, timeout=30):
    """Click the first 'Next' (crop dialog), with discard-popup detection."""
    next_btn_xpath = "(//div[@role='dialog']//div[@role='button'][normalize-space()='Next'])[1]"
    
    # We'll do up to 2 attempts if the discard popup appears
    for attempt in range(2):
        try:
            next_btn = WebDriverWait(bot, timeout).until(
                EC.element_to_be_clickable((By.XPATH, next_btn_xpath))
            )
        except Exception as e:
            print(f"ERROR: First 'Next' (crop) button not found/clickable: {e}")
            return False
        
        if try_click(bot, next_btn):
            time.sleep(1)
            # After clicking, check if discard popup showed up
            if check_and_cancel_discard_popup(bot, timeout=5):
                print("INFO: Retrying 'Next' click after discard popup was canceled.")
                continue  # retry
            print("INFO: Clicked the first 'Next' in the crop dialog.")
            return True
        else:
            # If we couldn't click, also check if discard popup is present
            if check_and_cancel_discard_popup(bot, timeout=5):
                print("INFO: Retrying 'Next' click after discard popup was canceled.")
                continue  # retry
            print("ERROR: Could not click the first 'Next' (crop dialog).")
            return False
    return False

def click_next_preview(bot, timeout=30):
    """
    Click the 'Next' button in the Edit dialog, with discard-popup detection.
    """
    next_btn_xpath = (
        "(//div[@aria-label='Edit' and @role='dialog']"
        "//div[@role='button' and normalize-space()='Next'])[1]"
    )

    for attempt in range(2):
        try:
            next_btn = WebDriverWait(bot, timeout).until(
                EC.element_to_be_clickable((By.XPATH, next_btn_xpath))
            )
        except Exception as e:
            print(f"ERROR: 'Next' (preview) button not found/clickable: {e}")
            return False
        
        if try_click(bot, next_btn):
            time.sleep(1)
            if check_and_cancel_discard_popup(bot, timeout=5):
                print("INFO: Retrying 'Next' (preview) click after discard popup was canceled.")
                continue
            print("INFO: Clicked the 'Next' button in Edit dialog.")
            return True
        else:
            if check_and_cancel_discard_popup(bot, timeout=5):
                print("INFO: Retrying 'Next' (preview) click after discard popup was canceled.")
                continue
            print("ERROR: Could not click the 'Next' button in Edit dialog.")
            return False
    return False

def click_share(bot, timeout=30):
    """Click the 'Share' button, with discard-popup detection."""
    share_btn_xpath = "//*[@role='button'][normalize-space()='Share'] | //button[normalize-space()='Share']"

    for attempt in range(2):
        try:
            share_btn = WebDriverWait(bot, timeout).until(
                EC.element_to_be_clickable((By.XPATH, share_btn_xpath))
            )
        except Exception as e:
            print(f"ERROR: 'Share' button not found: {e}")
            return False
        
        if try_click(bot, share_btn):
            time.sleep(1)
            if check_and_cancel_discard_popup(bot, timeout=5):
                print("INFO: Retrying 'Share' click after discard popup was canceled.")
                continue
            print("INFO: Clicked 'Share'.")
            return True
        else:
            if check_and_cancel_discard_popup(bot, timeout=5):
                print("INFO: Retrying 'Share' click after discard popup was canceled.")
                continue
            print("ERROR: Could not click 'Share' button.")
            return False
    return False

def wait_for_share_confirmation(bot, timeout=120):
    """Wait until 'Your reel has been shared.' is detected."""
    try:
        WebDriverWait(bot, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Your reel has been shared.')]"))
        )
        print("INFO: Share confirmation detected.")
        return True
    except Exception as e:
        print(f"ERROR: Share confirmation not detected within {timeout} seconds: {e}")
        return False

def upload_video(bot, folder_path):
    """Process: Create -> Select -> OS dialog -> Next(crop) -> Next(preview) -> Caption -> Share -> Confirm."""
    bot.get(PLATFORM_URL)
    time.sleep(1)
    
    # Click "Create"
    try:
        create_el = wait_clickable(bot, "//span[normalize-space()='Create']", 30)
        if not try_click(bot, create_el):
            print("ERROR: Cannot click 'Create' button.")
            return
        print("INFO: Clicked 'Create'.")
    except Exception as e:
        print(f"ERROR: 'Create' button not found: {e}")
        return
    time.sleep(1)
    
    # Click "Select from computer"
    try:
        select_el = wait_clickable(bot, "//button[normalize-space()='Select from computer']", 30)
        if not try_click(bot, select_el):
            print("ERROR: Cannot click 'Select from computer' button.")
            return
        print("INFO: Clicked 'Select from computer'.")
    except Exception as e:
        print(f"ERROR: 'Select from computer' button not found: {e}")
        return
    time.sleep(1)
    
    # OS file dialog using PyAutoGUI
    video_file = get_latest_video(folder_path)
    if not os.path.exists(video_file):
        print(f"ERROR: Video file not found -> {video_file}")
        return
    pyautogui.write(os.path.abspath(video_file))
    time.sleep(1)
    pyautogui.press('enter')
    print(f"INFO: Selected file: {video_file}")
    time.sleep(1)
    
    # First "Next" (crop dialog)
    if not click_next_crop(bot, 30):
        return

    # Second "Next" (preview dialog)
    if not click_next_preview(bot, 30):
        return
    time.sleep(1)
    
    # Paste description
    paste_description_into_caption(bot, folder_path)
    time.sleep(1)
    
    # Click "Share"
    if not click_share(bot, 30):
        return
    
    # Wait for confirmation
    if not wait_for_share_confirmation(bot, 120):
        print("ERROR: Upload confirmation not detected; process may not be complete.")
    else:
        print("INFO: Upload confirmed; post upload process completed.")

def main():
    if not os.path.exists(folder_path):
        print(f"ERROR: Folder path does not exist -> {folder_path}")
        sys.exit(1)
    bot = start_browser(CHANNEL_NAME)

    # We'll run the upload process in a separate thread so we can
    # enforce a 2-minute timeout at the main thread level.
    def process():
        try:
            upload_video(bot, folder_path)
        except Exception as e:
            print(f"ERROR in upload_video: {e}")

    t = threading.Thread(target=process)
    t.start()
    # Wait at most 120 seconds
    t.join(timeout=120)

    if t.is_alive():
        print("ERROR: Timed out after 2 minutes. Quitting browser.")
        try:
            bot.quit()
        except Exception:
            pass
    else:
        print("INFO: Upload process finished within 2 minutes. Quitting browser.")
        bot.quit()

    print("INFO: Done.")

if __name__ == "__main__":
    main()
