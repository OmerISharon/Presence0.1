"""
keyboard_switcher.py - A module to check and switch keyboard layouts to English
"""

import ctypes
from ctypes import wintypes
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Windows API constants
WM_INPUTLANGCHANGEREQUEST = 0x0050
HWND_BROADCAST = 0xFFFF
KL_ENGLISH_US = 0x04090409  # US English (0x0409)

# Load required DLLs
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Define necessary Windows API functions
user32.LoadKeyboardLayoutW.argtypes = [wintypes.LPCWSTR, wintypes.UINT]
user32.LoadKeyboardLayoutW.restype = wintypes.HANDLE

user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
user32.GetKeyboardLayout.restype = wintypes.HANDLE

user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL

def get_current_layout():
    """Get the current keyboard layout ID"""
    # 0 = foreground thread
    layout_id = user32.GetKeyboardLayout(0)
    primary_language_id = layout_id & 0x3FF  # Extract primary language ID
    logger.debug(f"Current keyboard layout: 0x{layout_id:08x}")
    logger.debug(f"Primary language ID: 0x{primary_language_id:04x}")
    return layout_id

def is_english():
    """Check if current keyboard layout is English"""
    layout_id = get_current_layout()
    # Get the lower word which contains the language ID
    language_id = layout_id & 0xFFFF
    
    # Common English language IDs:
    # 0x0409 = US English
    # 0x0809 = UK English
    # 0x0c09 = Australian English
    # 0x1009 = Canadian English
    english_ids = [0x0409, 0x0809, 0x0c09, 0x1009, 0x1409, 0x1809]
    
    return language_id in english_ids

def switch_to_english():
    """Switch the keyboard layout to US English"""
    try:
        # Check if already English
        if is_english():
            logger.info("Keyboard is already set to English")
            return True
        
        # Load the US English keyboard layout
        # "00000409" is the hex string for US English
        layout_handle = user32.LoadKeyboardLayoutW("00000409", 0)
        
        if layout_handle == 0:
            error = ctypes.get_last_error()
            logger.error(f"Failed to load English keyboard layout. Error code: {error}")
            return False
        
        # Send message to all windows to change input language
        # HWND_BROADCAST = message to all windows
        result = user32.PostMessageW(HWND_BROADCAST, 
                                    WM_INPUTLANGCHANGEREQUEST, 
                                    0, 
                                    KL_ENGLISH_US)
        
        if result == 0:
            error = ctypes.get_last_error()
            logger.error(f"Failed to switch to English keyboard. Error code: {error}")
            return False
            
        # Give some time for the change to take effect
        time.sleep(0.5)
        
        # Verify the change
        if is_english():
            logger.info("Successfully switched to English keyboard")
            return True
        else:
            logger.warning("Keyboard layout change command sent, but layout is still not English")
            return False
            
    except Exception as e:
        logger.error(f"Error switching keyboard layout: {e}")
        return False

# Create a class with properties for easier usage
class KeyboardLayout:
    @property
    def isEnglish(self):
        return is_english()
    
    def set_english(self):
        return switch_to_english()

# Create an instance that can be imported
keyboard = KeyboardLayout()

if __name__ == "__main__":
    # Enable debug logging when run directly
    # logger.setLevel(logging.DEBUG)
    # handler = logging.StreamHandler()
    # handler.setLevel(logging.DEBUG)
    # logger.addHandler(handler)
    
    # Check current layout
    current = get_current_layout()
    print(f"Current keyboard layout: 0x{current:08x}")
    print(f"Is English: {is_english()}")
    
    # Switch to English
    if not is_english():
        print("Switching to English keyboard layout...")
        result = switch_to_english()
        print(f"Switch result: {'Success' if result else 'Failed'}")
        print(f"Is English now: {is_english()}")
    else:
        print("Keyboard is already in English")