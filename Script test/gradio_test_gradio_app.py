import gradio as gr
import configparser
import os
import mido
import time

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

def update_midi_port(port):
    config = load_config()
    config['Parameters']['midi_port'] = port
    save_config(config)
    return f"MIDI port updated to: {port}"

def button_action():
    config = load_config()
    config['Parameters']['button_pressed'] = 'True'
    save_config(config)
    return "Button pressed! Action triggered in main script."

def get_status():
    # This function reads the status from main_script.py
    # For demonstration, we'll toggle a status every 5 seconds
    return "Active" if int(time.time()) % 10 < 5 else "Inactive"

midi_ports = mido.get_output_names()

with gr.Blocks() as iface:
    gr.Markdown("# MIDI Port Selection and Control")
    
    with gr.Row():
        midi_dropdown = gr.Dropdown(choices=midi_ports, label="Select MIDI Output Port")
        update_button = gr.Button("Update MIDI Port")
    
    output_text = gr.Textbox(label="Output")
    
    action_button = gr.Button("Trigger Action")
    
    status_text = gr.Textbox(label="Status", interactive=False)
    
    update_button.click(update_midi_port, inputs=midi_dropdown, outputs=output_text)
    action_button.click(button_action, inputs=None, outputs=output_text)
    
    def update_status():
        return get_status()
    
    status_text.change(update_status, inputs=None, outputs=status_text)
    
    # Update status every second
    gr.on(lambda: gr.Info("Status updated"), inputs=None, outputs=None, every=1)

if __name__ == "__main__":
    iface.launch()
