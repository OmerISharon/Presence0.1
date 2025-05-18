"""
TikTok Video Uploader – built on BaseUploader

• Supports headless/visible Chrome (stealth config unchanged).
• Handles a single MP4 + optional companion JSON (“description” field).
• Retries once if any step throws.
"""

from __future__ import annotations
import os, sys, time, json, logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
# Generic selenium helpers
# ──────────────────────────────────────────────────────────────
def wait_clickable(bot, xpath, timeout=60):
    return WebDriverWait(bot, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))


def wait_present(bot, by, ident, timeout=60):
    return WebDriverWait(bot, timeout).until(EC.presence_of_element_located((by, ident)))


def close_popups_if_any(bot):
    try:
        for el in bot.find_elements(By.XPATH, '//*[contains(@aria-label,"Close")]'):
            el.click(); time.sleep(0.3)
    except Exception:
        pass


def read_description(folder: str) -> str:
    for f in os.listdir(folder):
        if f.lower().endswith(".json"):
            try:
                with open(os.path.join(folder, f), encoding="utf‑8") as fh:
                    return json.load(fh).get("description", "")
            except Exception as e:
                logging.warning("Cannot read description JSON – %s", e)
    return ""


# ──────────────────────────────────────────────────────────────
# Concrete uploader
# ──────────────────────────────────────────────────────────────
class TikTokVideoUploader(BaseUploader):
    CLI_DESCRIPTION = "TikTok Video Uploader"

    # ---------- BaseUploader hooks ----------
    def setup(self) -> None:
        self.clear_screenshots(self.debug, self.headless, DEBUG_SCREENSHOTS_DIR)

        # Force media_type=video for now
        self.media_type = "video"

        self.bot = start_browser(
            self.channel_name,
            CHROME_BETA_USER_DATA_DIR,
            CHROME_BETA_EXE_PATH,
            headless=self.headless,
        )
        self.maximize_window(self.bot, self.headless)
        self.bot.get(PLATFORM_URL)                     # https://www.tiktok.com/upload

    def execute_steps(self) -> bool:
        """Upload the newest MP4 found in folder_path to TikTok."""
        video_path = self.get_latest_media()
        if not video_path:
            raise RuntimeError("No MP4 files in folder")

        description = read_description(self.folder_path)
        logging.info("Using video: %s", video_path)
        logging.info("Description: %s", description)

        # STEP 1 – choose file (headless or visible)
        try:
            file_input = wait_present(self.bot, By.CSS_SELECTOR, "input[type='file']", 60)
            file_input.send_keys(os.path.abspath(video_path))
            logging.info("STEP 1: Video path sent.")
        except Exception as e:
            raise RuntimeError(f"STEP 1: Cannot send file – {e}")

        time.sleep(5)
        close_popups_if_any(self.bot)

        # STEP 2 – fill description
        if description:
            self._replace_description(description)

        # STEP 3 – click Post
        try:
            post_btn = wait_clickable(self.bot, "//*[text()='Post']", 60)
            self.bot.execute_script("arguments[0].scrollIntoView({block:'center'});", post_btn)
            post_btn.click()
            logging.info("STEP 3: Clicked 'Post'.")
        except Exception as e:
            raise RuntimeError(f"STEP 3: Cannot click Post – {e}")

        # (Optional) wait for confirmation banner
        self.save_screenshot(self.bot, self.debug, self.headless, DEBUG_SCREENSHOTS_DIR, "TIKTOK_POST_CLICKED")
        time.sleep(3)   # adjust if you want a stronger confirmation check
        return True

    def teardown(self) -> None:
        self.save_screenshot(self.bot, self.debug, self.headless, DEBUG_SCREENSHOTS_DIR, "TIKTOK_FINISH")
        try:
            self.bot.quit()
        finally:
            logging.info("Browser closed – TikTok uploader finished.")

    # ---------- helpers ----------
    def _replace_description(self, text: str) -> None:
        """Clear the default filename placeholder and paste `text`."""
        try:
            # try locating by placeholder (filename) first, else generic editor
            video_name = os.path.splitext(os.path.basename(
                self.get_latest_media()))[0]

            try:
                desc_area = wait_present(
                    self.bot, By.XPATH,
                    f"//div[@contenteditable='true' and contains(@class,'public-DraftEditor-content') "
                    f"and .//span[text()='{video_name}']]", 60)
            except TimeoutException:
                desc_area = wait_present(
                    self.bot, By.XPATH,
                    "//div[@contenteditable='true' and contains(@class,'public-DraftEditor-content')]", 60)

            self.bot.execute_script("arguments[0].innerHTML='';", desc_area)
            desc_area.click(); time.sleep(0.3)
            desc_area.send_keys(Keys.CONTROL, "a"); desc_area.send_keys(Keys.BACKSPACE)
            desc_area.send_keys(text)
            logging.info("STEP 2: Description updated.")
        except Exception as e:
            logging.warning("STEP 2: Cannot update description – %s", e)


# ──────────────────────────────────────────────────────────────
# Entry‑point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    TikTokVideoUploader.main()
