import json
import mido
import time

# Load the instruments data
with open('BBCOrchestaInstruments.json', 'r') as f:
    instruments = json.load(f)

midi_ports = ["IAC Driver Bus 1 3", 'IAC Driver Bus 2 4']

def play_instrument(outport, instrument):
    print(f"Playing {instrument['name']}")
    for note in range(instrument['low_midi'], instrument['high_midi'] + 1):
        # Note on
        msg_on = mido.Message('note_on', note=note, velocity=64, 
                              channel=instrument['channel'] - 1, 
                              time=0)
        outport.send(msg_on)
        
        # Wait for a short duration
        time.sleep(0.1)
        
        # Note off
        msg_off = mido.Message('note_off', note=note, velocity=64, 
                               channel=instrument['channel'] - 1, 
                               time=0)
        outport.send(msg_off)
        
        # Small pause between notes
        time.sleep(0.05)

def all_notes_off(outport):
    for channel in range(16):
        msg = mido.Message('control_change', channel=channel, control=123, value=0)
        outport.send(msg)

def main():
    for instrument in instruments:
        port_index = instrument['midi']
        if port_index < len(midi_ports):
            with mido.open_output(midi_ports[port_index]) as outport:
                play_instrument(outport, instrument)
                all_notes_off(outport)
        else:
            print(f"No MIDI port available for {instrument['name']}")
        
        # Pause between instruments
        time.sleep(1)

if __name__ == "__main__":
    main()
