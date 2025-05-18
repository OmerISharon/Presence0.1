"""
Instagram‑Story uploader rewritten to use BaseUploader.

Run:
    python instagram_story_uploader.py <chrome_profile> <folder_path> [--headless] [--debug]
"""

import os
import sys
import time
from typing import Tuple
import pyautogui
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# project‑specific imports
from config import *
sys.path.insert(0, RESOURCES_DIR)
sys.path.insert(0, INTERNAL_MODULES_DIR)
sys.path.insert(0, UPLOADER_CLASSES)

from chrome_config import *
from uploaders.run_chrome_beta.run_chrome_beta import *

from base_uploader import BaseUploader

# ──────────────────────────────────────────────────────────────
# selenium step helpers (unchanged)
# ──────────────────────────────────────────────────────────────
import logging


def click_create_button(bot, timeout=5):
    try:
        svgs = WebDriverWait(bot, timeout).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "svg[aria-label='Home']")
            )
        )
    except TimeoutException:
        logging.error("STEP 1: No <svg aria-label='Home'> found within %ss.", timeout)
        raise RuntimeError("STEP 1: No <svg aria-label='Home'> found within %ss.", timeout)

    if not svgs:
        logging.error("STEP 1: Found 0 <svg aria-label='Home'> elements.")
        raise RuntimeError("STEP 1: Found 0 <svg aria-label='Home'> elements.")

    elem = svgs[0]
    try:
        elem.click()
        logging.info("STEP 1: Successfully clicked create button.")
        return True
    except WebDriverException as e:
        logging.warning("STEP 1: .click() failed, trying JS fallback – %s", e)
        try:
            bot.execute_script(
                "arguments[0].scrollIntoView(true); arguments[0].click();", elem
            )
            logging.info("STEP 1: JS fallback click successful.")
            return True
        except WebDriverException as je:
            logging.error("STEP 1: JS fallback also failed – %s", je)
            raise RuntimeError("STEP 1: JS fallback also failed – %s", je)


def click_story_button(bot, timeout=10, max_attempts=2):
    span_xpath = "//span[normalize-space()='Story']"
    input_xpath = "//input[@type='file']"

    for attempt in range(1, max_attempts + 1):
        try:
            logging.info("STEP 2: Attempt %d – locating Story button...", attempt)
            story_span = WebDriverWait(bot, timeout).until(
                EC.presence_of_element_located((By.XPATH, span_xpath))
            )

            try:
                story_span.click()
                logging.info("STEP 2: Story button clicked (standard).")
            except WebDriverException:
                bot.execute_script(
                    "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
                    story_span,
                )
                logging.info("STEP 2: Story button clicked via JS fallback.")

            try:
                file_input = WebDriverWait(bot, 3).until(
                    EC.presence_of_element_located((By.XPATH, input_xpath))
                )
                logging.info("STEP 2: File input element found (headless).")
                logging.info(file_input)

                return file_input
            except TimeoutException:
                logging.info("STEP 2: File input not found (likely visible mode).")
                return None

        except Exception as e:
            logging.warning("STEP 2: Attempt %d failed – %s", attempt, e)
            time.sleep(2)

    logging.error("STEP 2: All attempts to click Story button failed.")
    raise RuntimeError("STEP 2: All attempts to click Story button failed.")


def select_image(self, file_input=None):
    image_file = self.get_latest_media()
    if not image_file or not os.path.exists(image_file):
        logging.error("STEP 3: Image not found → %s", image_file)
        raise RuntimeError("STEP 3: Image not found → %s", image_file)

    abs_path = os.path.abspath(image_file)
    if file_input:
        try:
            file_input.send_keys(abs_path)
            logging.info("STEP 3: Image uploaded via input: %s", abs_path)
        except Exception as e:
            logging.error("STEP 3: Failed to send file in headless mode – %s", e)
            raise RuntimeError("STEP 3: Failed to send file in headless mode – %s", e)
    else:
        try:
            pyautogui.write(abs_path)
            time.sleep(1)
            pyautogui.press("enter")
            logging.info("STEP 3: Image selected via visible dialog: %s", abs_path)
        except Exception as e:
            logging.error("STEP 3: Failed to interact with file dialog – %s", e)
            raise RuntimeError("STEP 3: Failed to interact with file dialog – %s", e)


def click_add_to_your_story(bot, timeout=30):
    xpath = "//span[normalize-space()='Add to your story']"
    try:
        btn = WebDriverWait(bot, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        logging.info("STEP 4: Clicked 'Add to your story' button.")
        return True
    except Exception as e:
        logging.error("STEP 4: Failed to click 'Add to your story' – %s", e)
        raise RuntimeError("STEP 4: Failed to click 'Add to your story' – %s", e)


# ──────────────────────────────────────────────────────────────
# concrete uploader
# ──────────────────────────────────────────────────────────────
class InstagramStoryUploader(BaseUploader):
    CLI_DESCRIPTION = "Instagram Story Uploader"

    # ----- lifecycle hooks -----
    def setup(self) -> None:
        self.clear_screenshots(self.debug, self.headless, DEBUG_SCREENSHOTS_DIR)

        self.bot = start_browser_mobile(
            self.channel_name,
            CHROME_BETA_USER_DATA_DIR,
            CHROME_BETA_EXE_PATH,
            headless=self.headless,
        )
        self.maximize_window(self.bot, self.headless)
        self.bot.get(PLATFORM_URL)

    def execute_steps(self) -> None:
        # STEP 1
        click_create_button(self.bot)
        self.save_screenshot(
            self.bot,
            self.debug,
            self.headless,
            DEBUG_SCREENSHOTS_DIR,
            "STORY‑STEP‑1",
        )

        # STEP 2
        file_input = click_story_button(self.bot)
        self.save_screenshot(
            self.bot,
            self.debug,
            self.headless,
            DEBUG_SCREENSHOTS_DIR,
            "STORY‑STEP‑2",
        )

        # STEP 3
        select_image(self, file_input)
        self.save_screenshot(
            self.bot,
            self.debug,
            self.headless,
            DEBUG_SCREENSHOTS_DIR,
            "STORY‑STEP‑3",
        )

        # STEP 4
        click_add_to_your_story(self.bot)
        self.save_screenshot(
            self.bot,
            self.debug,
            self.headless,
            DEBUG_SCREENSHOTS_DIR,
            "STORY‑STEP‑4",
        )

        time.sleep(5)

    def teardown(self) -> None:
        self.save_screenshot(
            self.bot,
            self.debug,
            self.headless,
            DEBUG_SCREENSHOTS_DIR,
            "STORY‑FINISHED",
        )
        self.bot.quit()


# ──────────────────────────────────────────────────────────────
# entry‑point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    InstagramStoryUploader.main()
