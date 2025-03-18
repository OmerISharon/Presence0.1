
# -----------------------------------------------------------------
# GLOBAL IMPORTS
# -----------------------------------------------------------------

import sys

sys.path.insert(0, "D:\\2025\\Projects\\Presence\\Presence0.1\\Creator\\Configs")
from global_config import *
# IMPORTS: BASE_DIR, CREATOR_ROOT_DIR, CREATOR_CHANNELS_DIR, CHANNELS_DIR, GLOBAL_RESOURCES_DIR

# -----------------------------------------------------------------
# Configuration Variables
# -----------------------------------------------------------------

CHANNEL_NAME = "God Mode Notes"
ROOT_DIR = f"{CREATOR_CHANNELS_DIR}\\{CHANNEL_NAME}"
print(ROOT_DIR)

GPT_MODULE = "gpt-4.5-preview"

OPENAI_API_KEY_PATH = f"{BASE_DIR}\\..\\GlobalResources\\OPENAI_API_KEY.txt"
OPENAI_API_KEY = "OPENAI_API_KEY"

DEBUG_MODE = False
DEBUG_TEXT = "Hello from Debug Mode!"

DIR_OFFLINE_TEXT = f"{ROOT_DIR}\\Resources\\Text"
DIR_OFFLINE_TEXT_ARCHIVE = f"{ROOT_DIR}\\Resources\\Text - Archive"
PATH_PROMPT = f"{ROOT_DIR}\\Resources\\Prompt\\Main_Prompt.txt"

INCLUDE_TYPING_SOUNDS = True
TYPING_SOUNDS_DIR = f"{GLOBAL_RESOURCES_DIR}\\Audio\\Typing_Sounds\\Typing_Sounds_v3"
BACKGROUND_AUDIO = f"{ROOT_DIR}\\Resources\\Audio\\Background_Audio\\Root\\v1\\Full Audio.mp3"

OUT_BASE_FOLDER = f"{ROOT_DIR}\\Debug_Output" if DEBUG_MODE else f"{CHANNELS_DIR}\\{CHANNEL_NAME}\\Clips"

# Ancient effect overlay
ANCIENT_IMG = f"{ROOT_DIR}\\Resources\\Overlays\\ancient.jpg"

# Logo overlay
LOGO_PATH = f"{ROOT_DIR}\\Resources\\Avatar\\David-Goggins-no-background3.png"

# Font for Notepad
FONT_PATH = r"C:\\Windows\\Fonts\\consola.ttf"
FONT_SIZE = 48

# Video specs
WIDTH, HEIGHT = 1080, 1920
FPS = 60

# Make typing slower: about 70% speed => hold frames ~1 / 0.7 => ~1.4
# (i.e. if original hold was 5 frames, now it's ~7 frames)
SPEED_FACTOR = 4
