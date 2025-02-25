import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import *
sys.path.insert(0, RESOURCES_DIR)
from chrome_config import *

# Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
options.add_argument(f"--user-data-dir={CHROME_BETA_USER_DATA_DIR}")
options.add_argument("--profile-directory=Default")
options.binary_location = CHROME_BETA_EXE_PATH

def start_browser():
    service = Service(CHROME_BETA_DRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)

def wait_for_element(bot, by, identifier, timeout=30):
    return WebDriverWait(bot, timeout).until(EC.visibility_of_element_located((by, identifier)))

def find_account(bot, account_name, timeout=7):
    """
    Tries to locate an element that contains the account_name in different cases:
    original, upper, and lower. Returns the first matching element.
    """
    variants = [account_name, account_name.upper(), account_name.lower()]
    for variant in variants:
        xpath_expr = f'//*[contains(text(), "{variant}")]'
        try:
            # wait_for_element uses WebDriverWait internally.
            element = wait_for_element(bot, By.XPATH, xpath_expr, timeout=timeout)
            if element:
                print(f"INFO: Found account element using variant: {variant}")
                return element
        except Exception as e:
            print(f"ERROR: Variant '{variant}' not found, trying next variant...")
    return None

def switch_account(bot, account_name):
    print("INFO: Switching account")
    
    bot.get(PLATFORM_URL)
    time.sleep(5)
    
    # Step 4: Select the desired account from the list
    desired_account = find_account(bot, account_name)
    if desired_account:
        desired_account.click()
        time.sleep(5)
    else:
        print(f"ERROR: Desired account '{account_name}' not found using any case variant.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Please provide the account name as a parameter.")
        sys.exit(1)
    
    # Get the account name from the command-line arguments
    account_name = sys.argv[1]

    # Start the browser
    bot = start_browser()

    # Switch to the specified account
    switch_account(bot, account_name)

    bot.quit()

    print("INFO: Account switch process completed!")