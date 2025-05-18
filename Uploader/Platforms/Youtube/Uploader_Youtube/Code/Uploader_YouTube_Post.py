"""
YouTube Video Uploader – built on BaseUploader
• Headless‑friendly (uses <input type="file">)
• Expects one MP4 + optional JSON with “title” & “description”
• Retries once automatically via BaseUploader.run()
"""

from __future__ import annotations
import os, sys, time, json, logging
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
# Generic selenium helpers
# ──────────────────────────────────────────────────────────────
def wait_clickable(bot, xpath, timeout=60):
    return WebDriverWait(bot, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))


def wait_present(bot, by, ident, timeout=60):
    return WebDriverWait(bot, timeout).until(EC.presence_of_element_located((by, ident)))


def close_popups(bot):
    try:
        for el in bot.find_elements(By.XPATH, '//ytcp-button[contains(@aria-label,"Close")]'):
            el.click(); time.sleep(0.4)
    except Exception:
        pass


def read_json(folder: str) -> tuple[str, str]:
    """Return (title, description) from first JSON or ('','')."""
    for f in os.listdir(folder):
        if f.lower().endswith(".json"):
            try:
                with open(os.path.join(folder, f), encoding="utf‑8") as fh:
                    data = json.load(fh)
                    return data.get("title", ""), data.get("description", "")
            except Exception as e:
                logging.warning("Cannot read JSON – %s", e)
    return "", ""


# ──────────────────────────────────────────────────────────────
# Concrete uploader
# ──────────────────────────────────────────────────────────────
class YouTubeVideoUploader(BaseUploader):
    CLI_DESCRIPTION = "YouTube Video Uploader"

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

    def execute_steps(self) -> bool:
        video_path = self.get_latest_media()
        if not video_path:
            raise RuntimeError("No MP4 found in folder")

        title, description = read_json(self.folder_path)
        logging.info("Using file: %s", video_path)

        # STEP 1 – click upload icon
        try:
            upload_icon = wait_clickable(self.bot, "//*[@id='upload-icon']", 60)
            upload_icon.click()
        except Exception as e:
            raise RuntimeError(f"STEP 1: Cannot click upload icon – {e}")

        # STEP 2 – send file path
        try:
            file_input = wait_present(self.bot, By.CSS_SELECTOR, "input[type='file']", 60)
            file_input.send_keys(os.path.abspath(video_path))
            logging.info("STEP 2: File path sent.")
        except Exception as e:
            raise RuntimeError(f"STEP 2: Cannot send file – {e}")

        time.sleep(10); close_popups(self.bot)

        # STEP 3 – wait for processing (Next button enabled)
        if not self._wait_processing():
            raise RuntimeError("STEP 3: Processing timeout")

        # STEP 4 – fill title & description
        self._update_details(title, description)

        # STEP 5 – click Next ×3 then Done
        self._click_next_buttons()
        self._click_done()

        self.save_screenshot(self.bot, self.debug, self.headless, DEBUG_SCREENSHOTS_DIR, "YT_FINISH")
        return True

    def teardown(self) -> None:
        try:
            self.bot.quit()
        finally:
            logging.info("Browser closed – YouTube uploader finished.")

    # ---------- helpers ----------
    def _wait_processing(self, limit=600) -> bool:
        logging.info("STEP 3: Waiting for processing…")
        waited = 0
        while waited < limit:
            try:
                next_btn = self.bot.find_element(By.ID, "next-button")
                if next_btn.is_enabled():
                    logging.info("STEP 3: Processing complete.")
                    return True
            except Exception:
                pass
            time.sleep(10); waited += 10
            if waited % 120 == 0:
                logging.info("STEP 3: %ss elapsed – refreshing.", waited)
                self.bot.refresh(); time.sleep(5)
        return False

    def _update_details(self, title: str, description: str) -> None:
        if not (title or description):
            logging.info("STEP 4: No JSON metadata – skipping detail update.")
            return
        try:
            boxes = wait_present(self.bot, By.ID, "textbox", 60)  # returns first match
            boxes = self.bot.find_elements(By.ID, "textbox")
            if len(boxes) < 2:
                raise RuntimeError("Only one textbox found")

            title_box, desc_box = boxes[0], boxes[1]

            if title:
                title_box.clear(); title_box.send_keys(title)
            if description:
                desc_box.clear(); desc_box.send_keys(description)
            logging.info("STEP 4: Title/description set.")
        except Exception as e:
            logging.warning("STEP 4: Cannot update metadata – %s", e)

    def _click_next_buttons(self) -> None:
        for i in range(3):
            for attempt in range(3):
                try:
                    next_btn = wait_clickable(self.bot, '//ytcp-button[contains(@id,"next-button")]', 60)
                    self.bot.execute_script("arguments[0].scrollIntoView({block:'center'});", next_btn)
                    next_btn.click()
                    logging.info("STEP 5: Clicked Next (%d/3).", i + 1)
                    time.sleep(1.5)
                    break
                except Exception as e:
                    logging.warning("STEP 5: Next not clickable (try %d) – %s", attempt + 1, e)
                    self.bot.refresh(); time.sleep(5)

    def _click_done(self) -> None:
        try:
            done_btn = wait_clickable(self.bot, '//ytcp-button[contains(@id,"done-button")]', 60)
            self.bot.execute_script("arguments[0].scrollIntoView({block:'center'});", done_btn)
            done_btn.click()
            logging.info("STEP 6: Clicked Done.")
            time.sleep(3)
        except Exception as e:
            raise RuntimeError(f"STEP 6: Cannot click Done – {e}")


# ──────────────────────────────────────────────────────────────
# Entry‑point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    YouTubeVideoUploader.main()
