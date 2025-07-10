from gui import *
import ttkbootstrap as ttk
import configparser
from Settings import Settings

def main():
    settings = Settings()
    theme = settings.load_settings("DEFAULT", "theme")
    root = ttk.Window(themename=theme)
    app = GUI(root, settings)
    app.run()

if __name__ == "__main__":
    main()