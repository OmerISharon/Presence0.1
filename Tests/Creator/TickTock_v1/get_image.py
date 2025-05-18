import sys
import time
from httpcore import TimeoutException
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PLATFORM_URL = "https://www.instagram.com/"
INTERNAL_MODULES_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Internal_Modules"
RESOURCES_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Uploader\\Resources"
CHROME_PROFILE = "Omer"

sys.path.insert(0, INTERNAL_MODULES_DIR)
sys.path.insert(0, RESOURCES_DIR)
from chrome_config import *
from uploaders.run_chrome_beta.run_chrome_beta import *

def open_chatgpt_and_request_image(driver, prompt_text, download_folder=fr"C:\downloads"):
    """Send a prompt to ChatGPT to generate an image and download the result."""
    driver.get("https://chat.openai.com/")
    time.sleep(3)  # Allow page to load fully

    try:
        # === Locate ChatGPT editor ===
        editor = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//p[@data-placeholder="Ask anything"]'))
        )

        if editor.is_displayed() and editor.is_enabled():
            print("✅ Editor found. Sending image request...")
            driver.execute_script("arguments[0].click();", editor)
            time.sleep(0.5)

            # Inject prompt text via JS (ProseMirror-compatible)
            driver.execute_script(f"""
                const editor = arguments[0];
                const text = `{prompt_text}`;
                const event = new InputEvent('input', {{
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: text
                }});
                editor.textContent = text;
                editor.dispatchEvent(event);
            """, editor)

            time.sleep(0.5)
            editor.send_keys(Keys.ENTER)
            print("📨 Prompt sent. Waiting for image...")

            # === Wait for ChatGPT to respond with a message (assistant role) ===
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-message-author-role="assistant"]'))
            )

            print("🤖 Waiting for image to appear...")
            # Wait for the first image inside assistant reply
            image_element = WebDriverWait(driver, 180).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-message-author-role="assistant"]//img'))
            )

            # Get the image URL from the `src` attribute
            image_url = image_element.get_attribute("src")
            if image_url:
                print(f"🖼 Image URL: {image_url}")

                # Download image to disk
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Ensure the download folder exists
                    os.makedirs(download_folder, exist_ok=True)

                    # Save the image as a .jpg file
                    filename = os.path.join(download_folder, "chatgpt_image.jpg")
                    with open(filename, "wb") as f:
                        f.write(response.content)

                    print(f"✅ Image saved to: {filename}")
                else:
                    print(f"❌ Failed to download image. Status code: {response.status_code}")

            else:
                print("❌ Image URL not found or is invalid.")
            
            time.sleep(2)  # Give time to confirm download completion

        else:
            print("❌ ChatGPT input editor not interactable.")

    except TimeoutException:
        print("❌ Timeout: Couldn't find input or image in time.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        print("🛑 Closing browser...")
        driver.quit()
    

if __name__ == "__main__":
    # Example configuration
    PROMPT = "Generate a beautiful AI image of a futuristic city skyline at night."

    driver = start_browser(CHROME_PROFILE, CHROME_BETA_USER_DATA_DIR, CHROME_BETA_EXE_PATH)
    open_chatgpt_and_request_image(driver, PROMPT)
