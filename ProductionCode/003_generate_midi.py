
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

variable_ranges = {
    'WDIR': (0, 360),       # Wind direction in degrees
    'WSPD': (0, 14),        # Wind speed in m/s (adjust max as needed)
    'GST': (2, 16),         # Wind gust speed in m/s (adjust max as needed)
    'PRES': (1006, 1018),   # Atmospheric pressure in hPa
    'ATMP': (24, 30),       # Air temperature in °C
    'WTMP': (26, 31)        # Water temperature in °C
}

# Loading data
station_data, availability_df = load_buoy_data('buoy_data_20240601_to_20240915.h5')

# Example usage:
filtered_availability, filtered_station_data = filter_by_ocean(availability_df, station_data, buoy_df, "Indian Ocean")

# Usage
indian_ocean_music_base_dict = create_music_base_dict(filtered_station_data, variable_ranges, filtered_availability, output_octaves = 3)

tempo = 250
main_key = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


modes = ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian', 'Locrian']


midi_port_1 = "IAC Driver Bus 1 3"
midi_port_2 = "IAC Driver Bus 2 4"

# Live Configurable elements
tempo_range_low = 150
tempo_range_high = 250

data_to_play = 30

num_instruments_range_low = 3
num_instruments_range_high = 8


# Load the instruments data
with open('BBCOrchestaInstruments.json', 'r') as f:
    instruments = json.load(f)

print("Output ports:", mido.get_output_names())
print("Input ports:", mido.get_input_names())


midi_ports = [midi_port_1, midi_port_2]
outports = [mido.open_output(port) for port in midi_ports]

try:
    while True:
        n_channels = random.randint(num_instruments_range_low,num_instruments_range_high)
        print(n_channels)
        channel_data = create_random_channel_data(n_channels, filtered_availability, instruments)
        
        response = send_post_message(MSG_API, str(channel_data))
        print(channel_data)
        result = create_midi_progression(indian_ocean_music_base_dict, channel_data, random.choice(main_key), random.choice(modes),octaves=2)
        limited_result = [df.iloc[:data_to_play] for df in result]

        tempo = random.randint(tempo_range_low, tempo_range_high)
        play_midi_progression(limited_result, tempo, outports, channel_data, instruments)
        
        print("----------")
except KeyboardInterrupt:
    print("\nKeyboardInterrupt detected. Running cleanup code...")
    all_notes_off(outports)
finally:
    print("Program exiting.")






