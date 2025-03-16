# -----------------------------------------------------------------
# MetaData
# -----------------------------------------------------------------

CHANNEL_NAME = "RedNBlack"

# -----------------------------------------------------------------
# Paths & Directories
# -----------------------------------------------------------------

BASE_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1"
ROOT_DIR = f"{BASE_DIR}\\Creator\\{CHANNEL_NAME}"

DIR_OFFLINE_TEXT = f"{ROOT_DIR}\\Resources\\Text"
DIR_OFFLINE_TEXT_ARCHIVE = f"{ROOT_DIR}\\Resources\\Text - Archive"
PATH_PROMPT = f"{ROOT_DIR}\\Resources\\Prompt\\Main_Prompt.txt"

TYPING_SOUNDS_DIR = f"{ROOT_DIR}\\Resources\\Audio\\Typing_Sounds"


OUT_BASE_FOLDER = f"{BASE_DIR}\\Channels\\{CHANNEL_NAME}\\Clips"

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