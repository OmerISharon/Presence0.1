import os
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

# Function to wait for an element
def wait_for_element(bot, by, identifier, timeout=120):
    return WebDriverWait(bot, timeout).until(EC.element_to_be_clickable((by, identifier)))

# Function to close popups
def close_popups(bot):
    try:
        popups = bot.find_elements(By.XPATH, '//ytcp-button[contains(@aria-label, "Close")]')
        for popup in popups:
            popup.click()
            time.sleep(1)
    except:
        pass  # No pop-ups detected

# Function to get the latest video based on the naming pattern
def get_latest_video(directory, prefix="GOD MODE NOTE #", extension=".mp4"):
    files = os.listdir(directory)
    numbered_files = []

    for file in files:
        if file.startswith(prefix) and file.endswith(extension):
            try:
                number = int(file[len(prefix):-len(extension)])
                numbered_files.append((number, file))
            except ValueError:
                continue

    if not numbered_files:
        print(f"❌ ERROR: No files found matching pattern '{prefix}#' in {directory}")
        exit()

    # Get the file with the highest number
    latest_file = max(numbered_files, key=lambda x: x[0])[1]
    return os.path.join(directory, latest_file)

# Function to upload video
def upload_video(bot, video_path):
    print(f"🚀 Uploading: {video_path}")
    
    bot.get("https://studio.youtube.com")
    
    WebDriverWait(bot, 60).until(EC.presence_of_element_located((By.ID, "upload-icon")))
    upload_button = wait_for_element(bot, By.ID, "upload-icon")
    upload_button.click()
    time.sleep(3)

    file_input = WebDriverWait(bot, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    
    abs_path = os.path.abspath(video_path)
    if not os.path.exists(abs_path):
        print(f"❌ ERROR: File not found -> {abs_path}")
        bot.quit()
        return
    
    file_input.send_keys(abs_path)
    print("✅ Video file uploaded")
    time.sleep(10)

    close_popups(bot)
    print("⏳ Waiting for YouTube to finish processing...")

    processing_done = False
    wait_time = 0
    while wait_time < 600:
        try:
            next_button = bot.find_element(By.ID, "next-button")
            if next_button.is_enabled():
                print("✅ Video processing complete")
                processing_done = True
                break
        except:
            pass

        time.sleep(10)
        wait_time += 10

        if wait_time % 120 == 0:
            print("🔄 Refreshing page to check processing status...")
            bot.refresh()
            time.sleep(5)

    if not processing_done:
        print("❌ ERROR: Video processing took too long. Skipping.")
        bot.quit()
        return

    # Click "Next" three times
    for _ in range(3):
        retry_count = 0
        while retry_count < 3:
            try:
                next_button = WebDriverWait(bot, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//ytcp-button[contains(@id, "next-button")]'))
                )
                bot.execute_script("arguments[0].scrollIntoView();", next_button)
                time.sleep(1)
                bot.execute_script("arguments[0].click();", next_button)
                break
            except:
                print(f"🔄 'Next' button not found, refreshing page... ({retry_count + 1}/3)")
                bot.refresh()
                time.sleep(5)
                retry_count += 1

    # Click "Done"
    done_button = WebDriverWait(bot, 60).until(
        EC.element_to_be_clickable((By.XPATH, '//ytcp-button[contains(@id, "done-button")]'))
    )
    bot.execute_script("arguments[0].scrollIntoView();", done_button)
    time.sleep(1)
    bot.execute_script("arguments[0].click();", done_button)
    print("✅ Video successfully uploaded!")
    time.sleep(5)

# Directory containing video clips
video_dir = "C:\\Users\\omers\\Workshop\\Development\\AutoUpload\\Resources\\Clip_Prod"
if not os.path.exists(video_dir):
    print("❌ ERROR: 'videos' directory not found!")
    exit()

# Get the latest video based on the naming pattern
video_path = get_latest_video(video_dir)

bot = start_browser()
upload_video(bot, video_path)
bot.quit()

print("✅ Auto-upload completed!")
