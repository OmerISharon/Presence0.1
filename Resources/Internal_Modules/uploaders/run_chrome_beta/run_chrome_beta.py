import atexit
import json
import os
import pathlib
import re
import shutil
import socket
import sys
import tempfile
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth

# ──────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────

# helper – pick a free TCP port
def _free_port() -> int:
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

# helper – clone profile into temp dir
def _clone_profile(user_data_root: str, profile_dir: str) -> str:
    """
    Clone the entire <profile_dir> plus Local State into a temp
    user‑data directory *without* renaming the profile folder.
    """
    cleanup_old_temp_profiles()
    temp_root = pathlib.Path(tempfile.mkdtemp(prefix="presence_profile_"))

    # Local State (contains the cookie‑encryption key)
    shutil.copy2(pathlib.Path(user_data_root) / "Local State",
                 temp_root / "Local State")

    # full copy of the chosen profile, keep its original name
    src = pathlib.Path(user_data_root) / profile_dir
    dst = temp_root / profile_dir
    shutil.copytree(src, dst, dirs_exist_ok=True)

    return str(temp_root)

def cleanup_old_temp_profiles(prefix: str = "presence_profile_") -> None:
    """
    Remove *all* leftover temp user‑data directories from previous runs.

    • Looks in the system temp folder (tempfile.gettempdir())  
    • Deletes any directory whose name starts with `prefix`  
    • Silently ignores in‑use or already‑deleted folders
    """
    temp_dir   = pathlib.Path(tempfile.gettempdir())
    pattern    = re.compile(rf"^{re.escape(prefix)}", re.I)

    for entry in temp_dir.iterdir():
        try:
            if entry.is_dir() and pattern.match(entry.name):
                shutil.rmtree(entry, ignore_errors=True)
        except Exception:
            # in case the folder is in use or we lack permissions,
            # just move on; it will be cleaned up on a future run.
            pass

# ──────────────────────────────────────────────────────────────
# BROWSER ACTION FUNCTIONS
# ──────────────────────────────────────────────────────────────

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


# ──────────────────────────────────────────────────────────────
# BROWSER START HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────

def get_profile_directory(profile_name, chrome_user_data_dir):
    """Map the display profile name to the actual Chrome profile folder."""
    local_state_path = os.path.join(chrome_user_data_dir, "Local State")
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

def build_chrome_options(channel_name, chrome_user_data_dir, chrome_exe_path, headless=True, mobile=False):
    """Prepare ChromeOptions with isolated profile and common flags."""
    profile_dir = get_profile_directory(channel_name, chrome_user_data_dir)
    if not profile_dir:
        sys.exit("ERROR: Chrome profile not found.")

    isolated_user_data = _clone_profile(chrome_user_data_dir, profile_dir)

    options = webdriver.ChromeOptions()
    options.add_argument("--mute-audio")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--log-level=3")               # only FATAL
    options.add_argument("--disable-logging")           # mute stderr spam
    options.add_argument("--ignore-certificate-errors") # skips bad cert checks
    options.add_argument(f"--remote-debugging-port={_free_port()}")
    options.add_argument(f"--user-data-dir={isolated_user_data}")
    options.add_argument(f"--profile-directory={profile_dir}")

    if headless:
        options.add_argument("--headless=chrome")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        

    options.binary_location = chrome_exe_path
    return options


# ──────────────────────────────────────────────────────────────
# BROWSER START FUNCTIONS
# ──────────────────────────────────────────────────────────────

def start_browser(channel_name, chrome_user_data_dir, chrome_exe_path, headless=False):
    """Launch desktop Chrome (optionally headless), using a cloned profile."""

    options = build_chrome_options(channel_name, chrome_user_data_dir, chrome_exe_path, headless)

    driver = webdriver.Chrome(options=options)

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    if not headless:
        driver.maximize_window()

    time.sleep(1)
    return driver


def start_browser_mobile(channel_name,
                         chrome_user_data_dir,
                         chrome_exe_path,
                         headless=True):
    """Launch Chrome mobile emulation, isolating profile so multiple runs can coexist."""
    device_metrics = {
        "width": 390, "height": 844, "mobile": True,
        "deviceScaleFactor": 3,
        "screenOrientation": {"angle": 0, "type": "portraitPrimary"}
    }
    user_agent = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                  "Version/16.0 Mobile/15E148 Safari/604.1")

    options = build_chrome_options(channel_name, chrome_user_data_dir, chrome_exe_path, headless)

    # ----- start driver -----
    driver = webdriver.Chrome(options=options)

    # mobile emulation
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", device_metrics)
    driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {"userAgent": user_agent})
    driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {"enabled": True})

    return driver
