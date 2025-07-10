import configparser

SETTINGS_FILE = "settings.ini"

class Settings:
    def __init__(self):
        self.config = configparser.ConfigParser()

    def load_settings(self, section, key):
        self.config.read(SETTINGS_FILE)
        if self.config.has_option(section, key):
            return self.config.get(section,key)
        else:
            return None

    def save_settings(self, section, setting, value):
        config = configparser.ConfigParser()
        config.read(SETTINGS_FILE)
        if not config.has_section(section):
            config.add_section(section)
        config[section][setting] = value
        with open(SETTINGS_FILE, 'w') as configfile:
            config.write(configfile)