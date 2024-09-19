
import requests
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import random
import json
from music21 import pitch
from ndbc_api import NdbcApi
import mido
import time

def send_post_message(url, message='', headers=None):
    """
    Sends a JSON file via POST request.

    Parameters:
    url (str): The URL to send the POST request to.
    file_path (str): The path to the JSON file to be sent.
    headers (dict, optional): Additional headers to include in the request.

    Returns:
    requests.Response: The response object from the request.

    Raises:
    FileNotFoundError: If the specified JSON file is not found.
    json.JSONDecodeError: If the file is not valid JSON.
    requests.RequestException: For any network-related errors.
    """
    try:
        # Read the JSON file
        # with open(file_path, 'r') as file:
        #     data = json.load(file)
        data = {
            "message": message
        }
        # Set default headers if none provided
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            headers.setdefault('Content-Type', 'application/json')

        # Send POST request
        response = requests.post(url, json=data, headers=headers)

        # Raise an exception for bad status codes
        response.raise_for_status()

        return response

    except:
        print()
def randomize_array(arr):
    # Create a copy of the original array to avoid modifying it directly
    randomized = arr.copy()
    
    # Get the length of the array
    n = len(randomized)
    
    # Iterate through the array from the last element to the second element
    for i in range(n - 1, 0, -1):
        # Generate a random index from 0 to i (inclusive)
        j = random.randint(0, i)
        
        # Swap the elements at indices i and j
        randomized[i], randomized[j] = randomized[j], randomized[i]
    
    return randomized


def load_buoy_data(filename):
    with pd.HDFStore(filename) as store:
        availability_df = store['availability']
        station_data = {}
        for key in store.keys():
            if key.startswith('/station_'):
                station = key.split('_', 1)[1]
                station_data[station] = store[key]
    
    return station_data, availability_df

def filter_by_ocean(availability_df, cleaned_station_data, buoys_df, ocean_name):
    # Filter buoys_df to get stations from the specified ocean
    ocean_stations = buoys_df[buoys_df['Ocean'] == ocean_name]['Station'].tolist()

    # Filter availability_df
    filtered_availability = availability_df.loc[availability_df.index.intersection(ocean_stations)]
    
    # Remove columns filled with zero
    filtered_availability = filtered_availability.loc[:, (filtered_availability != 0).any(axis=0)]

    # Filter cleaned_station_data
    filtered_station_data = {station: data for station, data in cleaned_station_data.items() if station in ocean_stations}

    return filtered_availability, filtered_station_data

def create_music_base_dict(ocean_dict, variable_ranges, availability, output_octaves):
    ocean_music_base_dict = {}

    for station in availability.index:
        if station not in ocean_dict:
            continue

        df = ocean_dict[station]
        # Create a copy of the original dataframe, but only with columns that exist in both df and availability
        available_columns = [col for col in availability.columns if col in df.columns]
        normalized_df = df[available_columns].copy()

        for variable in available_columns:
            if availability.loc[station, variable] == 1:
                if variable not in variable_ranges:
                    print(f"Warning: {variable} not found in variable_ranges. Skipping.")
                    continue

                min_val, max_val = variable_ranges[variable]
                
                # Normalize the data
                normalized_df[variable] = (df[variable] - min_val) / (max_val - min_val)
                
                # Scale to the desired number of octaves
                normalized_df[variable] = normalized_df[variable] * (output_octaves * 7)
                
                # Round to nearest integer, but keep NaN values
                normalized_df[variable] = normalized_df[variable].apply(lambda x: round(x) if pd.notnull(x) else x)

        ocean_music_base_dict[station] = normalized_df

    return ocean_music_base_dict



def plot_music_base_dict(ocean_music_base_dict):
    # Determine the number of stations
    n_stations = len(ocean_music_base_dict)
    
    # Calculate the grid dimensions
    n_cols = 3  # You can adjust this for a different layout
    n_rows = (n_stations - 1) // n_cols + 1

    # Create a new figure
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5*n_rows))
    fig.suptitle("Normalized and Scaled Data for All Stations", fontsize=16)

    # Flatten the axes array for easier indexing
    axes = axes.flatten()

    for i, (station, df) in enumerate(ocean_music_base_dict.items()):
        ax = axes[i]
        
        # Plot each variable
        for column in df.columns:
            ax.plot(df.index, df[column], label=column)
        
        ax.set_title(f"Station: {station}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Scaled Value")
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True)

        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # Remove any unused subplots
    for j in range(i+1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()
    
# Define the intervals for each mode
modes = {
        'Ionian': [0, 2, 4, 5, 7, 9, 11],
        'Dorian': [0, 2, 3, 5, 7, 9, 10],
        'Phrygian': [0, 1, 3, 5, 7, 8, 10],
        'Lydian': [0, 2, 4, 6, 7, 9, 11],
        'Mixolydian': [0, 2, 4, 5, 7, 9, 10],
        'Aeolian': [0, 2, 3, 5, 7, 8, 10],
        'Locrian': [0, 1, 3, 5, 6, 8, 10]
    }

def get_midi_notes(mode='Ionian', midi_base=60, octaves=2):
    # Get the intervals for the specified mode
    intervals = modes.get(mode)
    
    if intervals is None:
        raise ValueError(f"Mode '{mode}' is not recognized.")
    # Create note mapping based on the input key and octave
    notes_midi = []
    for octave in range(octaves):
        notes_midi.extend([midi_base + interval + (octave * 12) for interval in intervals])

    return notes_midi

# Function to map a DataFrame column to MIDI notes
def map_to_midi(df_column, mode='Ionian', midi_base=0, octaves=2):
    midi_notes = get_midi_notes(mode, midi_base, octaves)
    # Map values from 0 to (7*octaves-1) to MIDI notes, casting to int
    midi_mapped = df_column.apply(lambda x: midi_notes[int(x)] if 0 <= x < 7*octaves and not pd.isna(x) else None)
    return midi_mapped

def create_midi_progression(music_base_dict, channel_data, main_key, mode, octaves=5):
    # Load instrument data
    with open('BBCOrchestaInstruments.json', 'r') as f:
        instruments = json.load(f)
    
    # Convert main_key to MIDI base note
    main_key_midi = pitch.Pitch(main_key).midi
    print(main_key_midi)
    
    # Initialize output list
    output_list = []
    
    # Process each channel
    for channel in channel_data:
        buoy = channel['buoy']
        print(buoy)
        variable = channel['variable']
        instrument_name = channel['instrument']
        
        # Get instrument data
        instrument = next((i for i in instruments if i['name'] == instrument_name), None)
        if not instrument:
            raise ValueError(f"Instrument {instrument_name} not found")
        
        # Find appropriate MIDI base
        low_midi = instrument['low_midi']
        high_midi = instrument['high_midi']
        
        # Calculate the first note in the instrument range that matches the main key
        midi_base = low_midi
        while midi_base % 12 != main_key_midi % 12:
            midi_base += 1
        
        # If the calculated midi_base is higher than the instrument's high_midi,
        # start from low_midi and go up by octaves until we're in range
        if midi_base > high_midi:
            midi_base = low_midi
            while midi_base % 12 != main_key_midi % 12:
                midi_base += 12
        
        # Ensure we have enough range for the specified number of octaves
        required_range = octaves * 12
        while midi_base + required_range > high_midi:
            midi_base -= 12
        
        # If we've gone below the low_midi, raise an error
        if midi_base < low_midi:
            print(f"Cannot fit {octaves} octaves within the instrument range")
        
        print(f"instrument:{instrument['name']}\nlow_midi:{low_midi}\nhigh_midi:{high_midi}\nmidi_base:{midi_base}\n")
        
        # Get data from the music_base_dict
        if buoy not in music_base_dict or variable not in music_base_dict[buoy].columns:
            raise ValueError(f"Data for buoy {buoy} and variable {variable} not found")
        
        data = music_base_dict[buoy][variable]
        
        # print(data)
        
        # Map data to MIDI notes
        midi_mapped = map_to_midi(data, mode=mode, midi_base=midi_base, octaves=octaves)
         
        print(midi_mapped)
        
        # Create DataFrame for this channel
        df = pd.DataFrame({f"{instrument_name}_{variable}": midi_mapped})
    
        # Fill NaN values with None
        df = df.where(pd.notnull(df), None)
    
        # Add DataFrame to output list
        output_list.append(df)
    
    return output_list
