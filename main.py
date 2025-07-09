from gui import *
import ttkbootstrap as ttk
import configparser

SETTINGS_FILE = "settings.ini"

def main():
    theme = load_settings()
    root = ttk.Window(themename=theme)
    app = GUI(root)
    app.run()

def load_settings():
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)
    return config['DEFAULT']['Theme']

def save_settings(section, setting, value):
    config = configparser.ConfigParser()
    config[section][setting] = value
    with open(SETTINGS_FILE, 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    main()