import ctypes
import time

# Constants
WM_INPUTLANGCHANGEREQUEST = 0x0050
HWND_BROADCAST = 0xFFFF
KL_ENGLISH_US = 0x04090409
ENGLISH_IDS = {0x0409, 0x0809, 0x0c09, 0x1009, 0x1409, 0x1809}

user32 = ctypes.WinDLL('user32', use_last_error=True)

def get_foreground_layout():
    hwnd = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(hwnd, None)
    return user32.GetKeyboardLayout(thread_id)

def is_english():
    return (get_foreground_layout() & 0xFFFF) in ENGLISH_IDS

def switch_to_english():
    if is_english():
        print("ℹ️  Keyboard is already set to English.")
        return True

    user32.LoadKeyboardLayoutW("00000409", 0)
    result = user32.PostMessageW(HWND_BROADCAST, WM_INPUTLANGCHANGEREQUEST, 0, KL_ENGLISH_US)

    if not result:
        print("❌ Failed to send layout switch command.")
        return False

    for _ in range(10):
        time.sleep(0.1)
        if is_english():
            print("✅ Keyboard layout switched to English.")
            return True

    print("❌ Layout change command sent, but it's still not in English.")
    return False

# Optional direct run
if __name__ == "__main__":
    switch_to_english()
