# main.py
import sys
import ctypes
import config
from gui.app import StravaApp

def main():
    # Set app ID for Windows taskbar icon resolution
    if sys.platform == 'win32':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(config.APP_ID) # noqa

    app = StravaApp()
    app.run()

if __name__ == "__main__":
    main()