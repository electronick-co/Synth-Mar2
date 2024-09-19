
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

# Usage
# plot_music_base_dict(indian_ocean_music_base_dict)

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
    {
        "buoy": "14049",
        "variable": "PRES",
        "instrument": "Tuba"
    }
]



# Load the instruments data
with open('instrumentos_all.json', 'r') as f:
    instruments = json.load(f)

# Assuming you have already created the filtered_availability dataframe
n_channels = 5  # or any number of channels you want


# Print the result
print(channel_data)

print("Output ports:", mido.get_output_names())
print("Input ports:", mido.get_input_names())


# Define the MIDI port (you may need to adjust this)
# port_name = 'IAC Driver Bus 1 3'
port_name = 'IAC Driver Bus 1 3'
# port_name = mido.open_output()
outport = mido.open_output(port_name)  # Replace with your MIDI output port name

tempo = 250
# print(limited_result)



channel_data = create_random_channel_data(n_channels, filtered_availability, instruments)
   
try:
    while True:
    # for _ in range(5):
        response = send_post_message(MSG_API, str(channel_data))

        result = create_midi_progression(indian_ocean_music_base_dict, channel_data, main_key, mode)
        # Assuming 'result' is an array of dataframes
        limited_result = [df.iloc[:100] for df in result]

        tempo = random.randint(200, 250)
        play_midi_progression(limited_result, tempo, outport)
        
        channel_data = create_random_channel_data(n_channels, filtered_availability, instruments)
        print("----------")

except KeyboardInterrupt:
    print("\nKeyboardInterrupt detected. Running cleanup code...")
    # stop all midi messages
    all_notes_off(outport)

finally:
    print("Program exiting.")






