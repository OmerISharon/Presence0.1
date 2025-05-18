"""
Facebook Reel Uploader – refactored to use BaseUploader

Run:
    python facebook_reel_uploader.py <chrome_profile> <media_folder>
           [--headless true|false] [--debug true|false]
"""

from __future__ import annotations
import os, sys, time, json, logging
import pyautogui

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import *
sys.path.insert(0, RESOURCES_DIR)
sys.path.insert(0, INTERNAL_MODULES_DIR)
sys.path.insert(0, UPLOADER_CLASSES)

from chrome_config import *
from uploaders.run_chrome_beta.run_chrome_beta import start_browser

from base_uploader import BaseUploader


# ──────────────────────────────────────────────────────────────
# Step‑specific helpers
# ──────────────────────────────────────────────────────────────

def get_description_from_json(folder_path: str) -> str:
    """Return the 'description' field from the first JSON in the folder, or empty."""
    for f in os.listdir(folder_path):
        if f.lower().endswith(".json"):
            try:
                with open(os.path.join(folder_path, f), encoding="utf‑8") as fh:
                    return json.load(fh).get("description", "")
            except Exception as e:
                logging.warning("Could not read description JSON – %s", e)
    return ""

# ──────────────────────────────────────────────────────────────
# Concrete uploader
# ──────────────────────────────────────────────────────────────
class FacebookReelUploader(BaseUploader):
    CLI_DESCRIPTION = "Facebook Reel Uploader"

    # ---------- BaseUploader hooks ----------
    def setup(self) -> None:
        self.clear_screenshots(self.debug, self.headless, DEBUG_SCREENSHOTS_DIR)
        self.media_type = "video"

        self.bot = start_browser(
            self.channel_name,
            CHROME_BETA_USER_DATA_DIR,
            CHROME_BETA_EXE_PATH,
            headless=self.headless,
        )
        self.maximize_window(self.bot, self.headless)
        self.bot.get(PLATFORM_URL)

    def execute_steps(self) -> None:
        # STEP 1
        try:
            create_reel_xpath = "//div[@role='button' and contains(@class, 'x1g2r6go') and .//i[contains(@style, 'background-image')]]"
            self._step_button_handler("Create Reel", 1, create_reel_xpath, DEBUG_SCREENSHOTS_DIR)
        except RuntimeError as e:
            raise RuntimeError(e)

        # STEP 2
        try:
            add_video_xpath = "//div[@role='button' and contains(@class, 'x1g2r6go') and .//div[contains(@style, 'mask-image')]]"
            self._step_button_handler("Add Video", 2, add_video_xpath, DEBUG_SCREENSHOTS_DIR, detect_dialog=True)
        except RuntimeError as e:
            raise RuntimeError(e)

        # # STEP 3
        # try:
        #     self._step_file_input_handler(3, DEBUG_SCREENSHOTS_DIR)
        # except RuntimeError as e:
        #     raise RuntimeError(e)
        
        # STEP 4
        try:
            description_textbox_xpath = "//div[contains(@class,'_5rp7')]//div[@role='textbox' and @contenteditable='true']"
            description = get_description_from_json(self.folder_path)
            self._step_textbox_handler(description, 4, description_textbox_xpath, DEBUG_SCREENSHOTS_DIR)
        except RuntimeError as e:
            pass

        time.sleep(3)

        # STEP 5
        try:
            first_next_button_xpath = "//div[@role='button' and (.//div[text()='הבא'] or .//div[text()='Next'])]"
            self._step_button_handler("First Next", 5, first_next_button_xpath, DEBUG_SCREENSHOTS_DIR)
        except RuntimeError as e:
            raise RuntimeError(e)

        # STEP 6
        try:
            second_next_button_xpath = "//div[@role='button' and (.//div[text()='הבא'] or .//div[text()='Next'])]"
            self._step_button_handler("Second Next", 6, second_next_button_xpath, DEBUG_SCREENSHOTS_DIR)
        except RuntimeError as e:
            raise RuntimeError(e)

        # STEP 7
        try:
            share_button_xpath = "//div[@role='button' and (.//div[text()='שיתוף'] or .//div[text()='Share'])]"
            self._step_button_handler("Share", 7, share_button_xpath, DEBUG_SCREENSHOTS_DIR)
        except RuntimeError as e:
            raise RuntimeError(e)
        

    def teardown(self) -> None:
        self.save_screenshot(self.bot, self.debug, self.headless, DEBUG_SCREENSHOTS_DIR, "Finish")
        try:
            self.bot.quit()
        except Exception:
            pass
        logging.info("Browser closed – uploader finished.")


# ──────────────────────────────────────────────────────────────
# Entry‑point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    FacebookReelUploader.main()
