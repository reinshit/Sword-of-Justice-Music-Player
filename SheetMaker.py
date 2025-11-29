# Transfer midi file to Keyboard sheet
import Player as GZP
import os

def printMidiSheet(m_file_name, m_key_add):
    """Generate sheet music notation from MIDI file"""
    # init
    ret = []
    cur = "1 "
    cur_time = 0
    cur_bar = 1
    
    # Add Path
    file_name = "." + os.sep + "midi_repo" + os.sep + m_file_name
    
    # Read midi_file
    try:
        midi_file = GZP.mido.MidiFile(file_name)
    except Exception as e:
        return [f"Error loading MIDI: {str(e)}"]
    
    # Show info
    for msg in midi_file:
        cur_time = msg.time + cur_time
        if cur_time >= 2:
            ret.append(cur)
            cur = ""
            cur_bar = cur_bar + 1
            cur = cur + str(cur_bar) + " "
            cur_time = 0
            
        if msg.type == "note_on":
            note = int(msg.note) + int(m_key_add)
            key = GZP.noteTrans(note)
            if key:
                cur = cur + key
            else:
                cur = cur + "?"  # Out of range indicator
    
    # Add last bar if not empty
    if cur.strip() and cur.strip() != str(cur_bar):
        ret.append(cur)
    
    return ret