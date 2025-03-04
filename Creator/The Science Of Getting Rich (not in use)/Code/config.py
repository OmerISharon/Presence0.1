# -----------------------------------------------------------------
# Configuration Variables
# -----------------------------------------------------------------

CHANNEL_NAME = "The Science Of Getting Rich (not in use)"
BASE_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1"
ROOT_DIR = f"{BASE_DIR}\\Creator\\{CHANNEL_NAME}"
GLOBAL_RESOURCES_DIR = f"{BASE_DIR}\\Resources\\Media_Resources"

OPENAI_API_KEY_PATH = f"{BASE_DIR}\\..\\GlobalResources\\OPENAI_API_KEY.txt"
OPENAI_API_KEY = "OPENAI_API_KEY"

DIR_OFFLINE_TEXT = f"{ROOT_DIR}\\Resources\\Text"
DIR_OFFLINE_TEXT_ARCHIVE = f"{ROOT_DIR}\\Resources\\Text - Archive"

TYPING_SOUNDS_DIR = f"{GLOBAL_RESOURCES_DIR}\\Audio\\Typing_Sounds"

DEBUG_MODE = False

OUT_BASE_FOLDER = f"{BASE_DIR}\\Channels\\{CHANNEL_NAME}\\Clips"
DEBUG_MODE_OUTPUT_DIR = f"{BASE_DIR}\\Channels\\{CHANNEL_NAME}\\Debug_Mode_Output"

FONT_PATH = r"C:\\Users\\omers\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Embolism Spark.ttf"
FONT_SIZE = 60

FONT_PATH_AUTHOR = r"C:\\Users\\omers\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Backstreet.ttf"
FONT_SIZE_AUTHOR = 50

FPS = 60 if DEBUG_MODE else 30

IMG_BOOK_COVER_PATH = f"{ROOT_DIR}\\Resources\\Images\\book_cover.jpg"
IMG_BLANK_PAGE_PATH = f"{ROOT_DIR}\\Resources\\Images\\blank_page.jpg"

QUOTE_JSON_PATH = f"{ROOT_DIR}\\Resources\\Quotes\\The_Science_of_Getting_Rich_ranked_quotes.json"

OUTPUT_FILENAME = "final_video.mp4"

# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Durations (in seconds)
DURATION_BOOK_COVER = 1       # Display book cover for 1 sec
DURATION_TRANSITION = 1       # Cross-fade duration from cover to blank page
DURATION_BLANK_FREEZE = 1     # Freeze on blank page for 1 sec
DURATION_TEXT_FREEZE = 3     # Freeze after text is complete

# Typing effect settings
TEXT_TO_TYPE = ("If you want to help the poor, demonstrate to them that they can become rich; "
                "prove it by getting rich yourself.")
TYPING_CPS = 15  # characters per second (programmer-like speed)

# Text placement settings
LEFT_MARGIN = 100
RIGHT_MARGIN = 100
TEXT_TOP = 200  # Vertical offset for text placement
TEXT_COLOR = (0, 0, 0)  # Black text

# Delay settings for typing (in seconds)
DELAY_LINE_BREAK = 0.5      # Extra delay when a line break (wrap) occurs
DELAY_SPECIAL_CHAR = 0.1    # Extra delay after special characters
SPECIAL_CHARS = {',', ';', ':', '.', '?', '!'}