from gui import *
import ttkbootstrap as ttk
import configparser
from settings import Settings

def main():
    settings = Settings()
    theme = settings.load_settings("LAST_SETTINGS", "theme")
    root = ttk.Window(themename=theme)
    root.iconbitmap("image.ico")
    app = GUI(root, settings)
    app.run()

if __name__ == "__main__":
    main()