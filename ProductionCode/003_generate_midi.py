
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
main_key = "C"
mode = "Mixolydian"




# Load the instruments data
with open('BBCOrchestaInstruments.json', 'r') as f:
    instruments = json.load(f)


print("Output ports:", mido.get_output_names())
print("Input ports:", mido.get_input_names())


midi_ports = ["IAC Driver Bus 1 3", 'IAC Driver Bus 2 4']
outports = [mido.open_output(port) for port in midi_ports]

try:
    while True:
        n_channels = random.randint(3,8)
        print(n_channels)
        channel_data = create_random_channel_data(n_channels, filtered_availability, instruments)
        
        response = send_post_message(MSG_API, str(channel_data))
        print(channel_data)
        result = create_midi_progression(indian_ocean_music_base_dict, channel_data, main_key, mode)
        limited_result = [df.iloc[:20] for df in result]

        tempo = random.randint(200, 250)
        play_midi_progression(limited_result, tempo, outports, channel_data, instruments)
        
        print("----------")
except KeyboardInterrupt:
    print("\nKeyboardInterrupt detected. Running cleanup code...")
    all_notes_off(outports)
finally:
    print("Program exiting.")






