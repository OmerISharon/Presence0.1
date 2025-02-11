import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
options.add_argument("user-data-dir=C:\\Users\\omers\\AppData\\Local\\Google\\Chrome Beta\\User Data\\")
options.binary_location = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"

def start_browser():
    service = Service(r"C:\\Users\\omers\\Workshop\\Development\\AutoUpload\\Resources\\Selenium\\chromedriver.exe")
    return webdriver.Chrome(service=service, options=options)

def wait_for_element(bot, by, identifier, timeout=30):
    return WebDriverWait(bot, timeout).until(EC.visibility_of_element_located((by, identifier)))

def switch_account(bot, account_name):
    print("🔧 Switching account")
    
    bot.get("https://youtube.com")
    time.sleep(5)

    # Step 1: Click on the channel icon
    channel_icon = wait_for_element(bot, By.ID, "avatar-btn")
    channel_icon.click()
    time.sleep(2)

    # Step 2: Click on "החלפת חשבון"
    switch_account_button = wait_for_element(bot, By.XPATH, '//*[contains(text(), "החלפת חשבון")]')
    switch_account_button.click()
    time.sleep(2)

    # Step 3: Click on "צפייה בכל הערוצים"
    switch_account_button = wait_for_element(bot, By.XPATH, '//*[contains(text(), "לצפייה בכל הערוצים")]')
    switch_account_button.click()
    time.sleep(2)
    
    # Step 4: Select the desired account from the list
    desired_account = wait_for_element(bot, By.XPATH, f'//*[contains(text(), "{account_name}")]')
    desired_account.click()
    time.sleep(5)

    print("✅ Successfully switched to the desired account!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ ERROR: Please provide the account name as a parameter.")
        sys.exit(1)
    
    # Get the account name from the command-line arguments
    account_name = sys.argv[1]

    # Start the browser
    bot = start_browser()

    # Switch to the specified account
    switch_account(bot, account_name)

    bot.quit()

    print("✅ Account switch process completed!")