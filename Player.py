import mido
import os
import time
import ctypes
from ctypes import wintypes

# Key Map between midi file and Keyboard
KEY_MAP = {60:'z',62:'x',64:'c',65:'v',67:'b',69:'n',71:'m',72:'a',74:'s',76:'d',77:'f',79:'g',81:'h',83:'j',84:'q',86:'w',88:'e',89:'r',91:'t',93:'y',95:'u',0:'p'}

SCALES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

# Scan midi file in mid_repo folder
def midScanner():
    m_file = os.listdir("."+os.sep+"midi_repo")
    ret = []
    for i in m_file:
        if os.path.splitext(i)[1] == '.mid':
            ret.append(i)
    return ret

# Translate midi note to keyboard
def noteTrans(m_note_value):
    return KEY_MAP.get(m_note_value, None)

# Check if note is in range
def isNoteInRange(note):
    return note in KEY_MAP

# Player only support melody in C Major, Use this to translate other scale to C Major
def allToCMajor(m_file_name):
    file_name = "." + os.sep + "midi_repo" + os.sep + m_file_name
    note_temp = []
    avialiable_add = []
    
    try:
        for msg in mido.MidiFile(file_name):
            if msg.type == "note_on":
                if msg.note not in note_temp:
                    note_temp.append(msg.note)
    except Exception as e:
        print(f"Error reading MIDI: {e}")
        return []

    for i in range(-48, 48):
        isC = True
        for cur in note_temp:
            if not KEY_MAP.__contains__(int(cur)+i):
                isC = False
                break
        if isC:
            avialiable_add.append(i)
    
    return avialiable_add

# Auto-adjust to best key when out of range
def findBestKey(m_file_name):
    """Find the key transposition that minimizes out-of-range notes"""
    file_name = "." + os.sep + "midi_repo" + os.sep + m_file_name
    note_temp = []
    
    try:
        for msg in mido.MidiFile(file_name):
            if msg.type == "note_on":
                if msg.note not in note_temp:
                    note_temp.append(msg.note)
    except Exception as e:
        print(f"Error reading MIDI: {e}")
        return 0
    
    best_key = 0
    best_score = float('inf')  # Lower is better
    
    # Try all possible transpositions
    for i in range(-48, 48):
        out_of_range_count = 0
        in_range_count = 0
        
        for cur in note_temp:
            transposed = int(cur) + i
            if KEY_MAP.__contains__(transposed):
                in_range_count += 1
            else:
                out_of_range_count += 1
        
        # Score: prioritize more in-range notes and penalize out-of-range
        # Also prefer transpositions closer to 0 (less pitch change)
        score = (out_of_range_count * 100) + abs(i)
        
        if score < best_score and in_range_count > 0:
            best_score = score
            best_key = i
    
    return best_key

# Check out of range notes
def getOutOfRangeNotes(m_file_name, m_key_add):
    file_name = "." + os.sep + "midi_repo" + os.sep + m_file_name
    out_of_range = []
    
    try:
        for msg in mido.MidiFile(file_name):
            if msg.type == "note_on":
                note = int(msg.note) + m_key_add
                if note not in KEY_MAP:
                    out_of_range.append(note)
    except Exception as e:
        print(f"Error checking range: {e}")
    
    return list(set(out_of_range))

# Get total MIDI duration
def getMidiDuration(m_file_name):
    file_name = "." + os.sep + "midi_repo" + os.sep + m_file_name
    try:
        midi = mido.MidiFile(file_name)
        return midi.length
    except:
        return 0

# SendInput related definitions
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


class MidiPlayer:
    """Enhanced MIDI player with pause/resume and real-time BPM control"""
    
    def __init__(self, file_name, bpm, key_add, allow_out_range=False):
        self.file_name = "." + os.sep + "midi_repo" + os.sep + file_name
        self.bpm = bpm
        self.key_add = key_add
        self.allow_out_range = allow_out_range
        self.is_paused = False
        self.should_stop = False
        self.pressed_keys = set()
        self.current_time = 0
        self.total_time = 0
        
        # Windows API setup
        self.SendInput = ctypes.windll.user32.SendInput
        self.MapVirtualKey = ctypes.windll.user32.MapVirtualKeyW
        
        # Load MIDI
        try:
            self.midi = mido.MidiFile(self.file_name)
            self.total_time = self.midi.length
        except Exception as e:
            raise Exception(f"Failed to load MIDI: {e}")
    
    def send_key(self, key, is_press):
        """Send keyboard input using SendInput"""
        if key is None:
            return
            
        vk_code = ord(key.upper())
        scan_code = self.MapVirtualKey(vk_code, 0)
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        
        flags = 0 if is_press else 0x0002
        ii_.ki = KeyBdInput(vk_code, scan_code, flags, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        self.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    
    def pause(self):
        """Pause playback"""
        self.is_paused = True
    
    def resume(self):
        """Resume playback"""
        self.is_paused = False
    
    def stop(self):
        """Stop playback"""
        self.should_stop = True
        # Release all pressed keys
        for key in list(self.pressed_keys):
            self.send_key(key, False)
        self.pressed_keys.clear()
    
    def set_bpm(self, new_bpm):
        """Change BPM in real-time"""
        self.bpm = max(40, min(2000, new_bpm))
    
    def play(self, progress_callback=None, note_callback=None):
        """Play MIDI with callbacks for progress and note visualization"""
        real_time = float(120 / self.bpm)
        
        for msg in self.midi:
            # Check for stop
            if self.should_stop:
                break
            
            # Handle pause
            while self.is_paused and not self.should_stop:
                time.sleep(0.01)
            
            # Update BPM dynamically
            real_time = float(120 / self.bpm)
            
            # Handle timing
            if msg.time > 0:
                time.sleep(float(msg.time) * real_time)
                self.current_time += msg.time
                
                if progress_callback:
                    progress_callback(self.current_time, self.total_time)
            
            # Handle note on
            if msg.type == "note_on" and msg.velocity > 0:
                note = int(msg.note) + self.key_add
                
                # Skip out of range notes if not allowed
                if not self.allow_out_range and note not in KEY_MAP:
                    continue
                
                key = noteTrans(note)
                if key:
                    self.send_key(key, True)
                    self.pressed_keys.add(key)
                    
                    if note_callback:
                        note_callback(key)
            
            # Handle note off
            elif (msg.type == "note_off") or (msg.type == "note_on" and msg.velocity == 0):
                note = int(msg.note) + self.key_add
                key = noteTrans(note)
                
                if key and key in self.pressed_keys:
                    self.send_key(key, False)
                    self.pressed_keys.remove(key)
        
        # Release any remaining keys
        for key in list(self.pressed_keys):
            self.send_key(key, False)
        self.pressed_keys.clear()


def counter(m_second):
    """Countdown timer"""
    for i in range(m_second):
        time.sleep(1)