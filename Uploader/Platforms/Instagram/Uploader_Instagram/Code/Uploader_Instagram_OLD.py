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
from selenium.common.exceptions import TimeoutException

from config import *
sys.path.insert(0, RESOURCES_DIR)
sys.path.insert(0, INTERNAL_MODULES_DIR)
from chrome_config import *
from uploaders.run_chrome_beta.run_chrome_beta import *

# ---

CHANNEL_NAME = sys.argv[1]
folder_path = sys.argv[2]

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
    """Click the first 'Next' in the crop dialog, retrying once if a discard popup appears."""
    next_btn_xpath = "(//div[@role='dialog']//div[@role='button'][normalize-space()='Next'])[1]"

    for attempt in range(2):
        try:
            btn = WebDriverWait(bot, timeout).until(
                EC.element_to_be_clickable((By.XPATH, next_btn_xpath))
            )
            if not try_click(bot, btn):
                print("ERROR: Click failed on 'Next' button.")
                return False
        except Exception as e:
            print(f"ERROR: 'Next' button not clickable: {e}")
            return False

        # if a discard popup appears, cancel it and retry immediately
        if check_and_cancel_discard_popup(bot, timeout=5):
            print("INFO: Discard popup canceled; retrying 'Next' click.")
            continue

        print("INFO: 'Next' clicked successfully.")
        return True

    print("ERROR: Unable to click 'Next' after retrying.")
    return False

def click_next_preview(bot, timeout=30, popup_timeout=5, max_attempts=2):
    """
    Click the 'Next' button in the Edit dialog, handling any discard confirmation pop-up.
    """
    xpath = (
        "(//div[@aria-label='Edit' and @role='dialog']"
        "//div[@role='button' and normalize-space()='Next'])[1]"
    )

    for _ in range(max_attempts):
        try:
            btn = WebDriverWait(bot, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        except TimeoutException as e:
            print(f"ERROR: 'Next' button not clickable: {e}")
            return False

        clicked = try_click(bot, btn)
        popped = check_and_cancel_discard_popup(bot, timeout=popup_timeout)

        if popped:
            print("INFO: Discard popup canceled, retrying.")
            continue

        if clicked:
            print("INFO: Clicked the 'Next' button in Edit dialog.")
            return True
        else:
            print("ERROR: Failed to click 'Next' (no popup to dismiss).")
            return False

    print("ERROR: Exhausted attempts to click 'Next'.")
    return False

def click_share(bot, timeout=30):
    """Click the 'Share' button specifically inside the floating modal dialog."""
    try:
        # Locate the modal first
        modal_xpath = "//div[@role='dialog' and @aria-label='Create new post']"
        modal = WebDriverWait(bot, timeout).until(
            EC.presence_of_element_located((By.XPATH, modal_xpath))
        )

        # Now find the Share button inside that modal
        share_btn_xpath = ".//div[@role='button' and normalize-space(text())='Share']"
        share_btn = WebDriverWait(modal, timeout).until(
            EC.element_to_be_clickable((By.XPATH, share_btn_xpath))
        )

        # Scroll into view and click (with JS fallback)
        bot.execute_script("arguments[0].scrollIntoView({block: 'center'});", share_btn)
        time.sleep(0.5)
        try:
            share_btn.click()
        except Exception as e:
            print(f"WARNING: Direct click failed: {e}, using JS click fallback.")
            bot.execute_script("arguments[0].click();", share_btn)

        time.sleep(1)
        if check_and_cancel_discard_popup(bot, timeout=5):
            print("INFO: Discard popup detected. Retry may be needed.")
            return False

        print("✅ Successfully clicked the correct 'Share' button.")
        return True

    except Exception as e:
        print(f"❌ ERROR: Could not click the correct 'Share' button: {e}")
        return False


def click_select_crop(bot, timeout=10):
    """
    Wait up to `timeout` seconds for the 'Select crop' SVG via original CSS selector,
    then click its parent using try_click for robust clicking.
    """
    css_selector = "div[class*='x9f619'] > svg[aria-label='Select crop']"
    try:
        svg = WebDriverWait(bot, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        parent = svg.find_element(By.XPATH, "./..")
        if try_click(bot, parent):
            print("INFO: Clicked 'Select crop' successfully.")
            return True
        else:
            print("ERROR: Could not click 'Select crop' element.")
            return False
    except TimeoutException:
        print(f"ERROR: 'Select crop' element not found after {timeout}s.")
        return False


def click_crop_portrait(bot, timeout=10):
    """
    Wait up to `timeout` seconds for the 'Crop portrait' SVG via original CSS selector,
    then click its ancestor using try_click for robust clicking.
    """
    css_selector = "svg[aria-label='Crop portrait icon']"
    try:
        svg = WebDriverWait(bot, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        clickable = svg.find_element(By.XPATH, "./../../..")
        if try_click(bot, clickable):
            print("INFO: Clicked 'Crop portrait' successfully.")
            return True
        else:
            print("ERROR: Could not click 'Crop portrait' element.")
            return False
    except TimeoutException:
        print(f"ERROR: 'Crop portrait' element not found after {timeout}s.")
        return False

def click_ok_button_if_exists(bot, timeout=5):
    """
    Tries up to 2 times to locate and click the 'OK' button using a single XPATH strategy.
    If not found within 5 seconds total, does nothing and continues script.
    """
    strategy = (By.XPATH, "//button[text()='OK']")
    strategy_desc = "By.XPATH with text 'OK'"
    attempts = 2
    wait_per_attempt = timeout // attempts

    for attempt in range(attempts):
        try:
            element = WebDriverWait(bot, wait_per_attempt).until(
                EC.presence_of_element_located(strategy)
            )
            element.click()
            print(f"INFO: Clicked OK button using strategy: {strategy_desc}")
            return True
        except Exception as e:
            print(f"DEBUG: Attempt {attempt+1} failed using {strategy_desc}: {e}")
            time.sleep(0.5)

    print("INFO: OK button not found after 2 attempts. Continuing script.")
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
    """Process: Create -> Select -> OS dialog -> [New events] -> Next(crop) -> Next(preview) -> Caption -> Share -> Confirm."""
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

    click_ok_button_if_exists(bot, 3)
    time.sleep(1)

    if not click_select_crop(bot, 30):
        return
    time.sleep(1)

    if not click_crop_portrait(bot, 30):
        return
    time.sleep(1)
    
    # First "Next" (crop dialog)
    if not click_next_crop(bot, 30):
        return
    time.sleep(1)

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
    bot = start_browser(CHANNEL_NAME, CHROME_BETA_USER_DATA_DIR, CHROME_BETA_EXE_PATH)

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