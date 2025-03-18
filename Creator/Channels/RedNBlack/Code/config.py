
# -----------------------------------------------------------------
# GLOBAL IMPORTS
# -----------------------------------------------------------------

import sys

sys.path.insert(0, "D:\\2025\\Projects\\Presence\\Presence0.1\\Creator\\Configs")
from global_config import *
# IMPORTS: BASE_DIR, CREATOR_ROOT_DIR, CREATOR_CHANNELS_DIR, CHANNELS_DIR, GLOBAL_RESOURCES_DIR

# -----------------------------------------------------------------
# MetaData
# -----------------------------------------------------------------

CHANNEL_NAME = "RedNBlack"

# -----------------------------------------------------------------
# Paths & Directories
# -----------------------------------------------------------------

ROOT_DIR = f"{CREATOR_CHANNELS_DIR}\\{CHANNEL_NAME}"

DIR_OFFLINE_TEXT = f"{ROOT_DIR}\\Resources\\Text"
DIR_OFFLINE_TEXT_ARCHIVE = f"{ROOT_DIR}\\Resources\\Text - Archive"
PATH_PROMPT = f"{ROOT_DIR}\\Resources\\Prompt\\Main_Prompt.txt"

TYPING_SOUNDS_DIR = f"{ROOT_DIR}\\Resources\\Audio\\Typing_Sounds"


OUT_BASE_FOLDER = f"{CHANNELS_DIR}\\{CHANNEL_NAME}\\Clips"

# -----------------------------------------------------------------
# CHATGPT
# -----------------------------------------------------------------

GPT_MODULE = "gpt-4.5-preview"

# -----------------------------------------------------------------
# Styling
# -----------------------------------------------------------------

FONT_PATH = r"C:\\Windows\\Fonts\\comicbd.ttf"
FONT_SIZE = 40

FADE_OUT_DURATION = 1.0

# -----------------------------------------------------------------
# MP4 Configurations
# -----------------------------------------------------------------

FPS = 60

# -----------------------------------------------------------------
# Scenario Flags
# -----------------------------------------------------------------

# Flag to choose post-typing animation style:
# Set to True to use the backspace animation (text is erased at twice the typing speed)
# Set to False to use the current fade-out style.
USE_BACKSPACE_STYLE = True