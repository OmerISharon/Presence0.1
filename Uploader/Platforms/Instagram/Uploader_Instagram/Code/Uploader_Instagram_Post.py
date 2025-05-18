"""
Instagram Post Uploader – refactored to use BaseUploader

Run:
    python instagram_post_uploader.py <chrome_profile> <media_folder>
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
# Generic selenium helpers
# ──────────────────────────────────────────────────────────────
def wait_clickable(bot, xpath, timeout=30):
    return WebDriverWait(bot, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))


def try_click(bot, element) -> bool:
    """Try clicking the element via ActionChains, then JS if needed."""
    try:
        ActionChains(bot).move_to_element(element).click().perform()
        return True
    except Exception:
        pass
    try:
        bot.execute_script(
            "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
            element,
        )
        return True
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────
# Step‑specific helpers
# ──────────────────────────────────────────────────────────────
def check_and_cancel_discard_popup(bot, timeout=5) -> bool:
    """If a 'Discard post?' popup appears, press 'Cancel' and return True."""
    try:
        dialog = WebDriverWait(bot, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@role='dialog']//*[contains(., 'Discard post')]")
            )
        )
        cancel_btn = dialog.find_element(By.XPATH, ".//button[contains(., 'Cancel')]")
        try_click(bot, cancel_btn)
        logging.info("STEP ?: Discard popup canceled.")
        return True
    except Exception:
        return False


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
class InstagramPostUploader(BaseUploader):
    CLI_DESCRIPTION = "Instagram Post Uploader"

    # ---------- BaseUploader hooks ----------
    def setup(self) -> None:
        self.clear_screenshots(self.debug, self.headless, DEBUG_SCREENSHOTS_DIR)

        self.bot = start_browser(
            self.channel_name,
            CHROME_BETA_USER_DATA_DIR,
            CHROME_BETA_EXE_PATH,
            headless=self.headless,
        )
        self.maximize_window(self.bot, self.headless)
        self.bot.get(PLATFORM_URL)

    def execute_steps(self) -> None:
        """High‑level workflow for posting a single video (reel) as in your legacy script."""
        # STEP 1: Click "Create"
        if not self._step_click_create():
            return

        # STEP 2: Click "Select from computer"  → maybe returns <input type=file>
        file_input = self._step_click_select_from_computer()

        # STEP 3: Select/upload the video file (headless vs. visible dialog)
        if not self._step_select_media(file_input):
            return

        # STEP 4: Handle crop mode (portrait) dialogs
        if not self._step_handle_crop_flow():
            return

        # STEP 5: Paste caption / description
        self._step_paste_description()

        # STEP 6: Share + wait confirmation
        self._step_share_and_confirm()

    def teardown(self) -> None:
        self.save_screenshot(
            self.bot,
            self.debug,
            self.headless,
            DEBUG_SCREENSHOTS_DIR,
            "POST‑FINISHED",
        )
        try:
            self.bot.quit()
        except Exception:
            pass
        logging.info("Browser closed – uploader finished.")

    # ---------- individual step implementations ----------
    def _step_click_create(self) -> bool:
        try:
            create_el = wait_clickable(
                self.bot, "//span[normalize-space()='Create']", 30
            )
            if not try_click(self.bot, create_el):
                logging.error("STEP 1: Cannot click 'Create'.")
                raise RuntimeError("STEP 1: Cannot click 'Create'.")

            logging.info("STEP 1: Clicked 'Create'.")
            time.sleep(1)
            self.save_screenshot(
                self.bot,
                self.debug,
                self.headless,
                DEBUG_SCREENSHOTS_DIR,
                "POST‑STEP‑1",
            )
            return True
        except Exception as e:
            logging.error("STEP 1: 'Create' not found – %s", e)
            raise RuntimeError("STEP 1: 'Create' not found – %s", e)

    def _step_click_select_from_computer(self):
        try:
            btn = wait_clickable(
                self.bot, "//button[normalize-space()='Select from computer']", 30
            )
            try_click(self.bot, btn)
            logging.info("STEP 2: Clicked 'Select from computer'.")
        except Exception as e:
            logging.error("STEP 2: Could not click 'Select from computer' – %s", e)
            raise RuntimeError("STEP 2: Could not click 'Select from computer' – %s", e)

        # look for an input[type=file] – headless path
        try:
            file_input = WebDriverWait(self.bot, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            logging.info("STEP 2: File‑input detected (headless).")
        except TimeoutException:
            file_input = None
            logging.info("STEP 2: No file‑input – using visible mode dialog.")

        self.save_screenshot(
            self.bot,
            self.debug,
            self.headless,
            DEBUG_SCREENSHOTS_DIR,
            "POST‑STEP‑2",
        )
        return file_input

    def _step_select_media(self, file_input):
        media_path = self.get_latest_media()
        if not media_path or not os.path.exists(media_path):
            logging.error("STEP 3: No %s found in %s", self.media_type, self.folder_path)
            raise RuntimeError("STEP 3: No %s found in %s", self.media_type, self.folder_path)

        abs_path = os.path.abspath(media_path)
        if file_input:  # ── headless: just send the path
            try:
                file_input.send_keys(abs_path)
                time.sleep(0.5)
                pyautogui.press("esc")
                logging.info("STEP 3: Uploaded %s via file‑input.", self.media_type)
            except Exception as e:
                logging.error("STEP 3: Failed to send file – %s", e)
                raise RuntimeError("STEP 3: Failed to send file – %s", e)
        else:  # ── visible: type in OS dialog, then force ‑close the dialog
            pyautogui.write(abs_path)
            time.sleep(0.7)
            pyautogui.press("enter")      # normal “Open” press
            time.sleep(0.7)

            # --- extra safety: press ESC in case dialog still lingers
            pyautogui.press("esc")
            time.sleep(0.3)
            logging.info("STEP 3: Selected %s via OS dialog and closed the dialog.", self.media_type)

        time.sleep(1)
        self.save_screenshot(
            self.bot,
            self.debug,
            self.headless,
            DEBUG_SCREENSHOTS_DIR,
            "POST‑STEP‑3",
        )
        self._click_ok_button_if_exists()
        return True

    # ---------- crop / edit flow ----------
    def _step_handle_crop_flow(self) -> bool:
        # Select‑crop  ▸ crop‑portrait  ▸ Next  ▸ Next
        if not self._click_select_crop():
            return False
        if not self._click_crop_portrait():
            return False
        if not self._click_next_crop():
            return False
        time.sleep(1)
        if not self._click_next_preview():
            return False
        return True

    # ---------- caption + share ----------
    def _step_paste_description(self) -> None:
        text = get_description_from_json(self.folder_path)
        if not text:
            logging.info("STEP 5: No caption text found – skipping caption.")
            return
        try:
            caption = WebDriverWait(self.bot, 30).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@aria-label='Write a caption...' and @role='textbox']",
                    )
                )
            )
            try_click(self.bot, caption)
            time.sleep(0.5)
            ActionChains(self.bot).send_keys(text).perform()
            logging.info("STEP 5: Caption pasted.")
        except Exception as e:
            logging.error("STEP 5: Could not paste caption – %s", e)
            raise RuntimeError("STEP 5: Could not paste caption – %s", e)
        self.save_screenshot(
            self.bot,
            self.debug,
            self.headless,
            DEBUG_SCREENSHOTS_DIR,
            "POST‑STEP‑5",
        )

    def _step_share_and_confirm(self):
        if not self._click_share():
            return
        self.save_screenshot(
            self.bot,
            self.debug,
            self.headless,
            DEBUG_SCREENSHOTS_DIR,
            "POST‑STEP‑6_SHARE_CLICKED",
        )
        if self._wait_for_share_confirmation():
            logging.info("STEP 6: Upload confirmed.")
        else:
            logging.error("STEP 6: No confirmation detected.")
            raise RuntimeError("STEP 6: No confirmation detected.")

    # ────────────────────────────────────────────────
    # Low‑level click helpers reused from original
    # (converted to logging + snake_case names)
    # ────────────────────────────────────────────────
    def _click_select_crop(self, timeout=30) -> bool:
        css = "div[class*='x9f619'] > svg[aria-label='Select crop']"
        try:
            svg = WebDriverWait(self.bot, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css))
            )
            if try_click(self.bot, svg.find_element(By.XPATH, "./..")):
                logging.info("STEP 4: Clicked 'Select crop'.")
                return True
        except TimeoutException:
            pass
        logging.error("STEP 4: 'Select crop' not found.")
        raise RuntimeError("STEP 4: 'Select crop' not found.")

    def _click_crop_portrait(self, timeout=30) -> bool:
        css = "svg[aria-label='Crop portrait icon']"
        try:
            svg = WebDriverWait(self.bot, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css))
            )
            if try_click(self.bot, svg.find_element(By.XPATH, "./../../..")):
                logging.info("STEP 4: Clicked 'Crop portrait'.")
                return True
        except TimeoutException:
            pass
        logging.error("STEP 4: 'Crop portrait' not found.")
        raise RuntimeError("STEP 4: 'Crop portrait' not found.")

    def _click_next_crop(self, timeout=30) -> bool:
        xpath = "(//div[@role='dialog']//div[@role='button'][normalize-space()='Next'])[1]"
        return self._click_next_generic(xpath, "Next (crop)", timeout)

    def _click_next_preview(self, timeout=30) -> bool:
        xpath = (
            "(//div[@aria-label='Edit' and @role='dialog']"
            "//div[@role='button' and normalize-space()='Next'])[1]"
        )
        return self._click_next_generic(xpath, "Next (preview)", timeout)

    def _click_next_generic(self, xpath, label, timeout) -> bool:
        try:
            btn = WebDriverWait(self.bot, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            if try_click(self.bot, btn):
                logging.info("STEP 4: Clicked '%s'.", label)
                return True
        except Exception as e:
            logging.error("STEP 4: '%s' not clickable – %s", label, e)
            raise RuntimeError("STEP 4: '%s' not clickable – %s", label, e)
        return False

    def _click_share(self, timeout=60) -> bool:
        try:
            modal = WebDriverWait(self.bot, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and @aria-label='Create new post']"))
            )
            share_btn = WebDriverWait(modal, timeout).until(
                EC.element_to_be_clickable((By.XPATH, ".//div[@role='button' and normalize-space()='Share']"))
            )
            self.bot.execute_script("arguments[0].scrollIntoView({block: 'center'});", share_btn)
            try:
                share_btn.click()
            except Exception:
                self.bot.execute_script("arguments[0].click();", share_btn)
            logging.info("STEP 6: Clicked 'Share'.")
            return True
        except Exception as e:
            logging.error("STEP 6: Could not click 'Share' – %s", e)
            raise RuntimeError("STEP 6: Could not click 'Share' – %s", e)


    def _click_ok_button_if_exists(self, timeout=5):
        try:
            ok_btn = WebDriverWait(self.bot, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//button[text()='OK']"))
            )
            ok_btn.click()
            logging.info("Clicked 'OK' button in intermediate dialog.")
        except Exception:
            pass

    def _wait_for_share_confirmation(self, timeout=120) -> bool:
        """
        Wait for Instagram's animated checkmark image to appear,
        indicating the post or reel was shared.
        """
        try:
            WebDriverWait(self.bot, timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//img[@alt='Animated checkmark']")
                )
            )
            return True
        except Exception as e:
            logging.error("No share confirmation image within %ss – %s", timeout, e)
            raise RuntimeError(f"No share confirmation image within {timeout}s")


# ──────────────────────────────────────────────────────────────
# Entry‑point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    InstagramPostUploader.main()
