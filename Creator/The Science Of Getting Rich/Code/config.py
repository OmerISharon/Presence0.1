# -----------------------------------------------------------------
# METADATA
# -----------------------------------------------------------------

CHANNEL_NAME = "The Science Of Getting Rich"
DEBUG_MODE = False
USE_KEYWORDS_BOLT_EFFECT = True

# -----------------------------------------------------------------
# GLOBAL DIRECTORIES & PATHS
# -----------------------------------------------------------------

BASE_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1"
ROOT_DIR = f"{BASE_DIR}\\Creator\\{CHANNEL_NAME}"
GLOBAL_RESOURCES_DIR = f"{BASE_DIR}\\Resources\\Media_Resources"

# -----------------------------------------------------------------
# OPENAI API
# -----------------------------------------------------------------

OPENAI_API_KEY_PATH = f"{BASE_DIR}\\..\\GlobalResources\\OPENAI_API_KEY.txt"
OPENAI_API_KEY = "OPENAI_API_KEY"

# -----------------------------------------------------------------
# CONTENT DIRECTORIES & PATHS
# -----------------------------------------------------------------

OUT_BASE_FOLDER = f"{BASE_DIR}\\Channels\\{CHANNEL_NAME}\\Clips"
DEBUG_MODE_OUTPUT_DIR = f"{BASE_DIR}\\Channels\\{CHANNEL_NAME}\\Debug_Mode_Output"

QUOTE_JSON_PATH = f"{ROOT_DIR}\\Resources\\Quotes\\The_Science_of_Getting_Rich_ranked_quotes.json"

DIR_OFFLINE_TEXT = f"{ROOT_DIR}\\Resources\\Text"
DIR_OFFLINE_TEXT_ARCHIVE = f"{ROOT_DIR}\\Resources\\Text - Archive"

TYPING_SOUNDS_DIR = f"{GLOBAL_RESOURCES_DIR}\\Audio\\Typing_Sounds\\Typing_Sounds_v3"

IMG_BOOK_COVER_PATH = f"{ROOT_DIR}\\Resources\\Images\\book_cover.jpg"
IMG_BLANK_PAGE_PATH = f"{ROOT_DIR}\\Resources\\Images\\blank_page.jpg"

# -----------------------------------------------------------------
# FONTS
# -----------------------------------------------------------------

FONT_PATH = r"C:\\Users\\omers\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Embolism Spark.ttf"
FONT_SIZE = 60

FONT_PATH_AUTHOR = r"C:\\Users\\omers\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Backstreet.ttf"
FONT_SIZE_AUTHOR = 50

# -----------------------------------------------------------------
# AUDIO
# -----------------------------------------------------------------

BACKGROUND_MUSIC_PATH = f"{GLOBAL_RESOURCES_DIR}\\Audio\\Ambience_Sounds\\Rain Heavy Quiet Interior.mp3"

OVERLAY_MUSIC_PATH = f"{GLOBAL_RESOURCES_DIR}\\Audio\\Overlay_Sounds\\intro-sound-180639_(lowervolume).mp3"
OVERLAY_MUSIC_DURATION = 2
OVERLAY_FADEOUT_DURATION = 1
OVERLAY_MUSIC_OFFSET = 0
OVERLAY_MUSIC_START_AT = 1

# -----------------------------------------------------------------
# TTS AUDIO
# -----------------------------------------------------------------

MODEL_NAME = "tts_models/en/vctk/vits"
SPEAKER_TYPE = "p267"
TTS_SPEED = 1
TTS_VOLUME = -10
TTS_ECHO_INTENSITY = 0.2

# -----------------------------------------------------------------
# CONTENT VARIABLES
# -----------------------------------------------------------------

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

FPS = 30 if DEBUG_MODE else 60

KEYWORD_COLOR = (187, 32, 36)

# SCENES DURATIOS
DURATION_BOOK_COVER = 1       # Display book cover
DURATION_TRANSITION = 1       # Cross-fade duration from cover to blank page
DURATION_BLANK_FREEZE = 2     # Freeze on blank page
DURATION_TEXT_FREEZE = 3     # Freeze after text is complete

TYPING_CPS = 20  # characters per second

# Text placement settings
LEFT_MARGIN = 100
RIGHT_MARGIN = 100
TEXT_TOP = 200  
TEXT_COLOR = (0, 0, 0)  # Black text

# Delay settings for typing (in seconds)
DELAY_LINE_BREAK = 0.5
DELAY_SPECIAL_CHAR = 0.1
SPECIAL_CHARS = {',', ';', ':', '.', '?', '!'}