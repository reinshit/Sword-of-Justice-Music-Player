"""
Thread classes for MIDI playback
"""
from PyQt5.QtCore import QThread, pyqtSignal
import Player as GZP
import win32gui


class PlaybackThread(QThread):
    """Background thread for MIDI playback"""
    progress_signal = pyqtSignal(float, float)
    finished_signal = pyqtSignal()
    note_played_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, file_name, keyadd, bpm, allow_out_range):
        super().__init__()
        self.file_name = file_name
        self.keyadd = keyadd
        self.bpm = bpm
        self.allow_out_range = allow_out_range
        self.player = None
        
    def run(self):
        try:
            # Activate game window
            hwnd = win32gui.FindWindow(None, "逆水寒手游桌面版")
            if hwnd:
                win32gui.SetForegroundWindow(hwnd)
                win32gui.SetActiveWindow(hwnd)
            
            # Create player instance
            self.player = GZP.MidiPlayer(self.file_name, self.bpm, self.keyadd, self.allow_out_range)
            
            # Play with callbacks
            self.player.play(
                progress_callback=self.progress_signal.emit,
                note_callback=self.note_played_signal.emit
            )
            
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def pause(self):
        if self.player:
            self.player.pause()
    
    def resume(self):
        if self.player:
            self.player.resume()
    
    def stop(self):
        if self.player:
            self.player.stop()
        self.terminate()
    
    def set_bpm(self, new_bpm):
        if self.player:
            self.player.set_bpm(new_bpm)