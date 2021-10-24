import time

import pyautogui
import pyperclip

if __name__ == "__main__":
    print('wait')
    time.sleep(2)
    print('copy')
    pyperclip.copy("可能性")
    print('paste')
    pyautogui.hotkey('ctrl', 'v')
