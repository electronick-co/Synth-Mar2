import configparser
import time
import os
import mido
import threading

CONFIG_FILE = 'config.ini'
DEFAULT_CONFIG = {
    'Parameters': {
        'midi_port': '',
        'button_pressed': 'False'
    }
}

def create_default_config():
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        create_default_config()
    
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

status = False

def toggle_status():
    global status
    while True:
        status = not status
        time.sleep(5)

def main():
    threading.Thread(target=toggle_status, daemon=True).start()
    
    while True:
        config = load_config()
        midi_port = config['Parameters']['midi_port']
        button_pressed = config['Parameters'].getboolean('button_pressed')
        
        print(f"Current MIDI port: {midi_port}")
        print(f"Button pressed: {button_pressed}")
        print(f"Current status: {status}")
        
        if button_pressed:
            print("Button was pressed! Performing action...")
            config['Parameters']['button_pressed'] = 'False'
            save_config(config)
        
        time.sleep(1)

if __name__ == "__main__":
    main()
