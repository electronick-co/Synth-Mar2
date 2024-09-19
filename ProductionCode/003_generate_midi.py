
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import random
import json

import json

from Synth_mar_lib import *

MSG_API = 'http://localhost:3000/api/messages'


# ReRading the df
buoy_df = pd.read_csv('buoys_with_ocean.csv')

# Loading data
station_data, availability_df = load_buoy_data('buoy_data_20240601_to_20240915.h5')

# Example usage:
filtered_availability, filtered_station_data = filter_by_ocean(availability_df, station_data, buoy_df, "Indian Ocean")

variable_ranges = {
    'WDIR': (0, 360),       # Wind direction in degrees
    'WSPD': (0, 14),        # Wind speed in m/s (adjust max as needed)
    'GST': (2, 16),         # Wind gust speed in m/s (adjust max as needed)
    'PRES': (1006, 1018),   # Atmospheric pressure in hPa
    'ATMP': (24, 30),       # Air temperature in °C
    'WTMP': (26, 31)        # Water temperature in °C
}

# Usage
indian_ocean_music_base_dict = create_music_base_dict(filtered_station_data, variable_ranges, filtered_availability, output_octaves = 3)

tempo = 250
main_key = "C"
mode = "Mixolydian"

channel_data = [
    {
        "buoy": "53056",
        "variable": "PRES",
        "instrument": "Piano",
    },
    {
        "buoy": "23014",
        "variable": "WTMP",
        "instrument": "Violins 1"
    },
    {
        "buoy": "14049",
        "variable": "PRES",
        "instrument": "Piccolo"
    },
]



# Load the instruments data
with open('BBCOrchestaInstruments.json', 'r') as f:
    instruments = json.load(f)

# Assuming you have already created the filtered_availability dataframe
n_channels = 2  # or any number of channels you want

print("Output ports:", mido.get_output_names())
print("Input ports:", mido.get_input_names())



def play_midi_progression(progression, tempo, outports, channel_data, instruments):
    delay = 60 / tempo  # seconds per beat
    current_notes = {}

    # Create a mapping of instrument names to their configurations
    instrument_config = {inst['name']: inst for inst in instruments}

    max_length = max(len(df) for df in progression)

    for i in range(max_length):
        for idx, df in enumerate(progression):
            if i < len(df):
                column_name = df.columns[0]
                note = df.iloc[i][column_name]
                
                instrument_name = channel_data[idx]['instrument']
                instrument = instrument_config[instrument_name]
                midi_port = outports[instrument['midi']]
                channel = instrument['channel'] - 1  # MIDI channels are 0-indexed
                print(f"MIDI Port: {instrument['midi']}, Channel: {channel}, Instrument: {instrument_name}")


                if pd.notna(note) and not np.isnan(note):
                    try:
                        note = int(note)
                    
                        if (midi_port, channel) in current_notes and current_notes[(midi_port, channel)] != note:
                            msg_off = mido.Message('note_off', note=current_notes[(midi_port, channel)], velocity=64, channel=channel)
                            midi_port.send(msg_off)
                        
                        if (midi_port, channel) not in current_notes or current_notes[(midi_port, channel)] != note:
                            msg_on = mido.Message('note_on', note=note, velocity=64, channel=channel)
                            midi_port.send(msg_on)
                            current_notes[(midi_port, channel)] = note
                    except ValueError:
                        pass
                
                elif (midi_port, channel) in current_notes:
                    msg_off = mido.Message('note_off', note=current_notes[(midi_port, channel)], velocity=64, channel=channel)
                    midi_port.send(msg_off)
                    del current_notes[(midi_port, channel)]

        time.sleep(delay)

    for (midi_port, channel), note in current_notes.items():
        msg_off = mido.Message('note_off', note=note, velocity=64, channel=channel)
        midi_port.send(msg_off)
    
    

def create_random_channel_data(n, filtered_availability, instruments):
    channel_data = []
    
    # Get unique buoys from filtered_availability index
    buoys = filtered_availability.index.unique()
    
    # Get list of instrument names
    instrument_names = [instrument['name'] for instrument in instruments]
    
    for _ in range(n):
        # Randomly select a buoy
        buoy = random.choice(buoys)
        
        # Get variables available for this buoy
        available_variables = filtered_availability.loc[buoy].index[filtered_availability.loc[buoy] == 1].tolist()
        
        # Randomly select a variable
        variable = random.choice(available_variables)
        
        # Randomly select an instrument
        instrument = random.choice(instrument_names)
        
        # Create channel data entry
        channel = {
            "buoy": buoy,
            "variable": variable,
            "instrument": instrument
        }
        
        channel_data.append(channel)
    
    return channel_data


def all_notes_off(outports):
    for outport in outports:
        for channel in range(16):
            for note in range(128):  # MIDI notes range from 0 to 127
                msg_off = mido.Message('note_off', note=note, velocity=0, channel=channel)
                outport.send(msg_off)
        outport.close()


midi_ports = ["IAC Driver Bus 1 3", 'IAC Driver Bus 2 4']
outports = [mido.open_output(port) for port in midi_ports]

n_channels = 2  # or any number of channels you want

try:
    while True:
        response = send_post_message(MSG_API, str(channel_data))
        
        channel_data = create_random_channel_data(n_channels, filtered_availability, instruments)
        print(channel_data)
        result = create_midi_progression(indian_ocean_music_base_dict, channel_data, main_key, mode)
        limited_result = [df.iloc[:100] for df in result]

        tempo = random.randint(200, 250)
        play_midi_progression(limited_result, tempo, outports, channel_data, instruments)
        
        print("----------")
except KeyboardInterrupt:
    print("\nKeyboardInterrupt detected. Running cleanup code...")
    all_notes_off(outports)
finally:
    print("Program exiting.")






