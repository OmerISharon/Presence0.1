import sys
import openai

# Load credentials
CREDENTIALS_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Credentials"
sys.path.insert(0, CREDENTIALS_DIR)
from credential_keys import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

response = openai.audio.speech.create(
    model="tts-1",  # or "tts-1-hd" for higher quality
    voice="nova",   # or "echo", "fable", "onyx", "shimmer", "alloy"
    input="Hey there! This is OpenAI's TTS engine speaking."
)

# Save the output
with open("output.mp3", "wb") as f:
    f.write(response.content)
