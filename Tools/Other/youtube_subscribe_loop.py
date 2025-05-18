import os
import time
import sys
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

INTERNAL_MODULES_DIR = fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules"
RESOURCES_DIR = fr"D:\2025\Projects\Presence\Presence0.1\Uploader\Resources"

sys.path.insert(0, RESOURCES_DIR)
from chrome_config import *
sys.path.insert(0, INTERNAL_MODULES_DIR)
from uploaders.run_chrome_beta.run_chrome_beta import *

# ---- CONFIGURATION ---- #
channel_url = "https://www.youtube.com/@GodModeNotes"  # <- Replace with your actual channel URL

# ------------------------ #

def subscribe_to_channel(bot, profile_name):
    try:
        bot.get(channel_url)
        wait = WebDriverWait(bot, 10)

        # Look for the subscribe button via structural class path
        sub_button = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//div[contains(@class, 'yt-subscribe-button-view-model-wiz__container')]//button[not(@disabled)]"
        )))

        # Click the button
        bot.execute_script("arguments[0].click();", sub_button)
        print(f"✅ Subscribed with profile: {profile_name}")
        time.sleep(2)

    except Exception as e:
        print(f"❌ Error for {profile_name}: {str(e)}")
    finally:
        bot.quit()


if __name__ == "__main__":
    channels_dir = fr"D:\2025\Projects\Presence\Presence0.1\Channels"
    profile_names = [name for name in os.listdir(channels_dir) if os.path.isdir(os.path.join(channels_dir, name))]

    for profile_name in profile_names:
        print(f"🚀 Launching browser with profile: {profile_name}")
        browser = start_browser(profile_name, CHROME_BETA_USER_DATA_DIR, CHROME_BETA_EXE_PATH)
        if browser:
            subscribe_to_channel(browser, profile_name)
        time.sleep(1)
