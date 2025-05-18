"""
Reusable abstract uploader.

Each concrete uploader:
1.  Inherits from `BaseUploader`.
2.  Implements `setup()` and `execute_steps()`.
3.  (Optionally) overrides `add_extra_arguments()` or any hook.
"""

from __future__ import annotations
import argparse
import datetime
import os
import sys
import logging
from abc import ABC, abstractmethod
import time
from typing import Callable, List, Tuple, Optional

import pyautogui
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as se

Strategy = Tuple[str, Callable[[], WebElement]]

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)

class BaseUploader(ABC):
    """Common CLI, helpers and workflow for every uploader script."""

    # ────────────────────────────────
    # Construction / CLI
    # ────────────────────────────────
    CLI_DESCRIPTION: str = "Generic Uploader"

    def __init__(self,
                 channel_name: str,
                 folder_path: str,
                 media_type: str = "video",
                 headless: bool = True,
                 debug: bool = False) -> None:
        self.channel_name = channel_name
        self.folder_path = folder_path
        self.media_type = media_type
        self.headless = headless
        self.debug = debug
        self._validate_folder()

    # ---------- CLI ----------
    @classmethod
    def parse_arguments(cls) -> argparse.Namespace:
        """Parse arguments common to every uploader + subclass‑specific ones."""
        parser = argparse.ArgumentParser(description=cls.CLI_DESCRIPTION)
        parser.add_argument("channel_name", type=str, help="Chrome profile name")
        parser.add_argument("folder_path", type=str, help="Path to media folder")
        parser.add_argument("--media_type", type=str, default="video", help="Media type of the media file (video, image, text)")
        parser.add_argument("--headless", type=lambda s: s.lower() in {"true", "1", "yes"}, default=True, help="Run in headless mode (default: True)")
        parser.add_argument("--debug", type=lambda s: s.lower() in {"true", "1", "yes"}, default=False, help="Run in debug mode (default: False)")
        cls.add_extra_arguments(parser)                 # optional hook
        return parser.parse_args()

    @classmethod
    def add_extra_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """Hook for subclasses that need additional CLI flags."""
        ...

    # ────────────────────────────────
    # Helpers
    # ────────────────────────────────
    def get_latest_media(self):
        ext_map: dict[str, Tuple[str, ...]] = {
            "image": (".jpg", ".jpeg", ".png", ".gif"),
            "video": (".mp4", ".mov", ".avi", ".mkv"),
            "text":  (".txt", ".md", ".rtf"),
        }

        # 1️⃣ Determine which extensions to look for
        if self.media_type:                                    # specific category
            exts = ext_map.get(self.media_type.lower())
            if not exts:
                raise ValueError(f"Unsupported media_type '{self.media_type}'")
        else:                                             # all categories
            exts = tuple(sum(ext_map.values(), ()))       # flatten tuples

        # 2️⃣ Collect matching files (skip *tmp* artifacts)
        files = [
            f for f in os.listdir(self.folder_path)
            if f.lower().endswith(exts) and "tmp" not in f.lower()
        ]
        if not files:
            logging.error("No media files found in %s", self.folder_path)
            raise RuntimeError("No media files found in %s", self.folder_path)

        # 3️⃣ Pick the newest by creation time
        latest = max(files,
                    key=lambda f: os.path.getctime(os.path.join(self.folder_path, f)))
        return os.path.join(self.folder_path, latest)

    # ────────────────────────────────
    # Workflow
    # ────────────────────────────────
    def run(self) -> None:
        """Main workflow; retry once on failure."""
        self.setup_logging()
        print(f"\n📢 {self.CLI_DESCRIPTION}{' [DEBUG]' if self.debug else ''}\n")

        attempts = 1 if self.debug else 2

        for attempt in range(1, attempts + 1):
            self.setup()
            try:
                if self.execute_steps() is False:
                    raise RuntimeError("execute_steps() reported failure")
                break  # Success
            except Exception as e:
                logging.error(f"Attempt {attempt}/{attempts} failed: {e}", exc_info=True)
                self.teardown()
                if attempt == attempts:
                    logging.error("All retries exhausted. Aborting.")
                    raise
                logging.info("Retrying…")

        self.teardown()

    @abstractmethod
    def setup(self) -> None:
        """Prepare everything (browser, credentials, etc.)."""
        ...

    @abstractmethod
    def execute_steps(self) -> None:
        """Perform the concrete upload actions (step #1, #2, …)."""
        ...

    def teardown(self) -> None:          # optional to override
        """Close resources, take final screenshots, …"""
        logging.info("Finished – nothing to clean up.")

    # ────────────────────────────────
    # Steps Event Handlers
    # ────────────────────────────────

    def try_click(self, element) -> bool:
        """Try clicking the element via ActionChains, then JS if needed."""
        try:
            ActionChains(self.bot).move_to_element(element).click().perform()
            return True
        except Exception:
            pass
        try:
            self.bot.execute_script(
                "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
                element,
            )
            return True
        except Exception:
            return False
        
    def wait_present(self, by, ident, timeout=60):
        return WebDriverWait(self.bot, timeout).until(EC.presence_of_element_located((by, ident)))
        

    def _install_file_dialog_detector(self):
        js = r"""
            if (!window.__fileDialogEvents__) {
                window.__fileDialogEvents__  = [];   // meta info
                window.__fileDialogInputs__  = [];   // actual elements
                (function () {
                    const orig = HTMLInputElement.prototype.click;
                    HTMLInputElement.prototype.click = function () {
                        if (this.type === 'file') {
                            window.__fileDialogEvents__.push({type:'click', time:Date.now()});
                            window.__fileDialogInputs__.push(this);   // <-- keep the element
                        }
                        return orig.apply(this, arguments);
                    };

                    new MutationObserver(muts => muts.forEach(m => m.addedNodes.forEach(n => {
                        const add = el => {
                            window.__fileDialogEvents__.push({type:'added', time:Date.now()});
                            window.__fileDialogInputs__.push(el);
                        };
                        if (n.tagName==='INPUT' && n.type==='file') add(n);
                        if (n.querySelectorAll)
                            n.querySelectorAll('input[type=file]').forEach(add);
                    }))).observe(document.body, {childList:true, subtree:true});
                })();
            }
            // clear buffers for a fresh run
            window.__fileDialogEvents__.length  = 0;
            window.__fileDialogInputs__.length  = 0;
        """
        self.bot.execute_script(js)

    def _wait_file_dialog_events(self, timeout=10):
        try:
            WebDriverWait(self.bot, timeout).until(
                lambda d: d.execute_script("return window.__fileDialogEvents__?.length>0;"))
        except Exception:
            return []
        return self.bot.execute_script("""
            const ev = window.__fileDialogEvents__ || [];
            window.__fileDialogEvents__ = [];
            return ev;
        """)

    # ------------------------------------------------------------------
    # 2) Upload helper – finds the latest <input type="file"> and feeds it
    # ------------------------------------------------------------------
    def _send_file_to_latest_input(self, abs_path: str, timeout: int = 5):
        """
        Retrieves the most-recent file-input element that triggered the dialog
        (captured by the JS patch) and sends ``abs_path`` to it.
        """
        try:
            WebDriverWait(self.bot, timeout).until(
                lambda d: d.execute_script("return window.__fileDialogInputs__?.length>0;"))
        except Exception:
            raise RuntimeError("No captured file-input available to receive the path.")

        # pull the newest element reference (returns as Selenium WebElement)
        target = self.bot.execute_script("return window.__fileDialogInputs__.pop();")

        # make sure Selenium can interact even if it’s hidden
        self.bot.execute_script("""
            arguments[0].style.display='block';
            arguments[0].style.visibility='visible';
            arguments[0].style.opacity=1;
        """, target)

        target.send_keys(abs_path)
        logging.info("🟢 File path sent to captured <input>: %s", abs_path)

    # ------------------------------------------------------------------
    # 3) One-stop step handler ---- call with upload_path=abs_path
    # ------------------------------------------------------------------
    def _step_button_handler(
            self, element_name: str, step_num: int, xpath: str,
            screenshots_dir: str, finish_delay: int = 1,
            detect_dialog: bool = False):

        if detect_dialog:
            self._install_file_dialog_detector()   # must happen *before* click

        # click the button
        element = WebDriverWait(self.bot, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        if not self.try_click(element):
            raise RuntimeError(fr"STEP {step_num}: Couldn't click {element_name} Button.")

        # diagnostics
        self.save_screenshot(self.bot, self.debug, self.headless, screenshots_dir, fr"STEP {step_num} - {element_name} clicked")

        if finish_delay > 0:
            time.sleep(finish_delay)

        # wait for the dialog + optionally upload
        if detect_dialog:
            events = self._wait_file_dialog_events()
            logging.info(f"STEP {step_num}: File-dialog events: {events}")

            media_path = self.get_latest_media()
            abs_path = os.path.abspath(media_path)
            if abs_path:
                self._send_file_to_latest_input(abs_path)
                logging.info(f"STEP {step_num}: Send file into File-dialog: {abs_path}")

        if finish_delay > 0:
            time.sleep(finish_delay)


    # def _step_file_input_handler(self, step_num: int, screenshots_dir: str):
    #     media_path = self.get_latest_media()
    #     abs_path = os.path.abspath(media_path)

    #     try:
    #         if file_input and self.headless:
    #             logging.info(fr"STEP {step_num}: file_input found: {file_input}")
    #             file_input.send_keys(abs_path)
    #         else:
    #             pyautogui.write(abs_path)
    #             pyautogui.press("enter")
    #             pyautogui.press("esc")            

    #         logging.info(fr"STEP {step_num}: abs path sent to file input: {abs_path}")

    #     except Exception as e:
    #         err_msg = fr"""STEP {step_num}: File-input failed"
    #         "{e}"""
    #         logging.error(err_msg)
    #         raise RuntimeError(err_msg)
            
    #     logging.info(fr"STEP {step_num}: Selected file successfully.")
    #     self.save_screenshot(self.bot, self.debug, self.headless, screenshots_dir, fr"STEP {step_num} - File Input Event")
    #     time.sleep(5)
    

    def _step_textbox_handler(self, text: str, step_num: int, xpath: str, screenshots_dir: str):
        if not text:
            err_msg = fr"STEP {step_num}: No text found."
            logging.error(err_msg)
            raise RuntimeError(err_msg)
        
        try:
            element = WebDriverWait(self.bot, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))

            if not self.try_click(element):
                err_msg = fr"STEP {step_num}: Could not click on textbox."
                logging.error(err_msg)
                raise RuntimeError(err_msg)

            ActionChains(self.bot).send_keys(text).perform()
            logging.info(fr"STEP {step_num}: Text pasted.")
        
        except Exception:
            err_msg = fr"STEP {step_num}: Error while pasting text."
            logging.error(err_msg)
            raise RuntimeError(err_msg)

        logging.info(fr"STEP {step_num}: Pasted text successfully")
        self.save_screenshot(self.bot, self.debug, self.headless, screenshots_dir, fr"STEP {step_num} - Textbox Event")
        time.sleep(1)
        
    # ────────────────────────────────
    # Utilities
    # ────────────────────────────────
    def _validate_folder(self) -> None:
        if not os.path.exists(self.folder_path):
            logging.error("Folder path does not exist → %s", self.folder_path)
            sys.exit(1)
        else:
            logging.info("Folder path validated successfully → %s", self.folder_path)

    @staticmethod
    def maximize_window(bot, headless_mode: bool) -> None:
        """Maximize the browser window (only in non-headless mode)."""
        if not headless_mode:
            bot.maximize_window()

    @staticmethod
    def save_screenshot(bot, debug_mode: bool, headless_mode: bool,
                        output_dir: str, step_name: str) -> None:
        """Save screenshot for debug purposes (only in headless + debug mode)."""
        if debug_mode and headless_mode:
            path = os.path.join(output_dir, f"{step_name}.png")
            bot.save_screenshot(path)
            logging.info(f"Saved debug screenshot: {path}")

    @staticmethod
    def clear_screenshots(debug_mode: bool, headless: bool, output_dir: str) -> None:
        """Delete .png screenshots from the output folder if in debug mode."""
        if debug_mode and headless and os.path.exists(output_dir):
            deleted = 0
            for f in os.listdir(output_dir):
                if f.lower().endswith(".png"):
                    try:
                        os.remove(os.path.join(output_dir, f))
                        deleted += 1
                    except Exception as e:
                        logging.warning(f"Could not delete {f}: {e}")
            logging.info(f"Deleted {deleted} screenshot(s) from {output_dir}")

    def setup_logging(self) -> None:
        """Configure logging to both CLI and timestamped log file."""
        log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        formatter  = logging.Formatter(log_format)

        # ── console ─────────────────────────────────────────────
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # ── file ────────────────────────────────────────────────
        timestamp        = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_description = self.CLI_DESCRIPTION.replace(" ", "_")

        log_dir = os.path.join(
            fr"D:\2025\Projects\Presence\Presence0.1\Channels",
            self.channel_name,
            "Logs",
            "Uploader",
            safe_description,
        )
        os.makedirs(log_dir, exist_ok=True)

        # 👉 prefix “DEBUG_” when debug mode is on
        prefix   = "DEBUG_" if self.debug else ""
        log_path = os.path.join(log_dir, f"{prefix}{timestamp}.log")

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)

        # ── register handlers ───────────────────────────────────
        logging.root.handlers.clear()                 # avoid duplicates
        logging.basicConfig(level=logging.INFO, handlers=[stream_handler, file_handler])

        logging.info("Logging initialized → %s", log_path)


    # ---------- Convenience entry‑point ----------
    @classmethod
    def main(cls) -> None:
        args = cls.parse_arguments()
        uploader = cls(args.channel_name,
                       args.folder_path,
                       args.media_type,
                       args.headless,
                       args.debug)
        uploader.run()
