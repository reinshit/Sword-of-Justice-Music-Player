"""
SoJ Music Player 
"""
import sys
import os
import json
import shutil
import ctypes

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox,
                             QCheckBox, QProgressBar, QFrame, QSpinBox, QShortcut,
                             QTextEdit, QListWidget, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QKeySequence, QFont
import Player as GZP
import SheetMaker as GSM
from threads import PlaybackThread
from widgets import NoteVisualization
from hotkeys import HotkeyManager
from themes import get_theme


def is_admin():
    try:
        if os.sep == '/':
            return True
        else:
            return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class ModernGUI(QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.dark_mode = True
        self.playThread = None
        self.is_playing = False
        self.is_paused = False
        self.key_adds = []
        self.settings_file = "settings.json"
        self.hotkey_manager = HotkeyManager()
        
        self.init_ui()
        
        self.load_settings()
        self.apply_theme()
        self.setup_shortcuts()
        self.setup_global_hotkeys()
        
    def init_ui(self):
        self.setWindowTitle("Sword Of Justice Music Player")
        self.setMinimumSize(800, 600)
        
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.create_header(main_layout)
        self.create_divider(main_layout)
        self.create_visualization(main_layout)
        self.create_controls(main_layout)
        self.create_progress(main_layout)
        self.create_playback_buttons(main_layout)
        self.create_sheet_section(main_layout)
        self.create_status_bar(main_layout)
        
        self.refresh_midi_list()
    
    def create_header(self, layout):
        header_layout = QHBoxLayout()
        
        title = QLabel("🎵 SOJ Music Player")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        if self.hotkey_manager.is_available():
            self.label_hotkey = QLabel("⌨️ Global Hotkeys: Ctrl+V (Play/Pause) | Ctrl+B (Stop)")
            self.label_hotkey.setStyleSheet("color: #00ff00; font-weight: bold;")
            header_layout.addWidget(self.label_hotkey)
        
        self.dark_mode_btn = QPushButton("🌙 Dark")
        self.dark_mode_btn.setFixedSize(80, 35)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        header_layout.addWidget(self.dark_mode_btn)
        
        layout.addLayout(header_layout)
    
    def create_divider(self, layout):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)
    
    def create_visualization(self, layout):
        self.note_viz = NoteVisualization(self)
        layout.addWidget(self.note_viz)
    
    def create_controls(self, layout):
        controls = QFrame()
        controls_layout = QVBoxLayout(controls)
        
        file_header = QHBoxLayout()
        file_header.addWidget(QLabel("MIDI Files:"))
        file_header.addStretch()
        
        self.btn_add_midi = QPushButton("➕ Add MIDI")
        self.btn_add_midi.setFixedSize(110, 30)
        self.btn_add_midi.clicked.connect(self.add_midi_file)
        file_header.addWidget(self.btn_add_midi)
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(40, 30)
        self.btn_refresh.clicked.connect(self.refresh_midi_list)
        self.btn_refresh.setToolTip("Refresh MIDI list")
        file_header.addWidget(self.btn_refresh)
        
        controls_layout.addLayout(file_header)
        
        self.list_midi = QListWidget()
        self.list_midi.setMaximumHeight(150)
        self.list_midi.itemClicked.connect(self.midi_selected)
        controls_layout.addWidget(self.list_midi)
        
        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(5)  
        
        settings_layout.addWidget(QLabel("Key:"))
        self.combo_key = QComboBox()
        self.combo_key.setEnabled(False)
        settings_layout.addWidget(self.combo_key)
        
        self.btn_auto_key = QPushButton("🎯 Auto")
        self.btn_auto_key.setFixedSize(80, 30)
        self.btn_auto_key.setEnabled(False)
        self.btn_auto_key.setToolTip("Auto-adjust to best key")
        self.btn_auto_key.clicked.connect(self.auto_adjust_key)
        settings_layout.addWidget(self.btn_auto_key)
        
        settings_layout.addSpacing(400) 
        
        bpm_label = QLabel("BPM:")
        settings_layout.addWidget(bpm_label)
        self.spin_bpm = QSpinBox()
        self.spin_bpm.setRange(40, 2000)
        self.spin_bpm.setValue(120)
        self.spin_bpm.setEnabled(False)
        self.spin_bpm.valueChanged.connect(self.bpm_changed)
        settings_layout.addWidget(self.spin_bpm)
        
        settings_layout.addSpacing(10)
        
        wait_label = QLabel("Wait:")
        settings_layout.addWidget(wait_label)
        self.spin_wait = QSpinBox()
        self.spin_wait.setRange(0, 20)
        self.spin_wait.setValue(3)
        self.spin_wait.setSuffix("s")
        settings_layout.addWidget(self.spin_wait)
        
        settings_layout.addStretch()  
        
        controls_layout.addLayout(settings_layout)
        
        options_layout = QHBoxLayout()
        self.check_out_range = QCheckBox("Allow out-of-range notes")
        self.check_out_range.setChecked(False)
        options_layout.addWidget(self.check_out_range)
        options_layout.addStretch()
        controls_layout.addLayout(options_layout)
        
        layout.addWidget(controls)
    
    def create_progress(self, layout):
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.label_time = QLabel("00:00 / 00:00")
        self.label_time.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.label_time)
        
        layout.addWidget(progress_frame)
    
    def create_playback_buttons(self, layout):
        playback_layout = QHBoxLayout()
        playback_layout.addStretch()
        
        self.btn_play = QPushButton("▶ Play\n(Ctrl+V)")
        self.btn_play.setFixedSize(140, 50)
        self.btn_play.setEnabled(False)
        self.btn_play.clicked.connect(self.play_clicked)
        playback_layout.addWidget(self.btn_play)
        
        self.btn_pause = QPushButton("⏸ Pause\n(Ctrl+V)")
        self.btn_pause.setFixedSize(140, 50)
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.pause_clicked)
        playback_layout.addWidget(self.btn_pause)
        
        self.btn_stop = QPushButton("⏹ Stop\n(Ctrl+B)")
        self.btn_stop.setFixedSize(140, 50)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_clicked)
        playback_layout.addWidget(self.btn_stop)
        
        playback_layout.addStretch()
        layout.addLayout(playback_layout)
    
    def create_sheet_section(self, layout):
        sheet_frame = QFrame()
        sheet_layout = QVBoxLayout(sheet_frame)
        
        sheet_header = QHBoxLayout()
        sheet_header.addWidget(QLabel("Sheet Preview:"))
        sheet_header.addStretch()
        
        self.btn_show_sheet = QPushButton("Generate Sheet")
        self.btn_show_sheet.clicked.connect(self.show_sheet)
        self.btn_show_sheet.setEnabled(False)
        sheet_header.addWidget(self.btn_show_sheet)
        
        self.btn_copy_sheet = QPushButton("Copy to Clipboard")
        self.btn_copy_sheet.clicked.connect(self.copy_sheet)
        sheet_header.addWidget(self.btn_copy_sheet)
        
        sheet_layout.addLayout(sheet_header)
        
        self.text_sheet = QTextEdit()
        self.text_sheet.setReadOnly(True)
        self.text_sheet.setMaximumHeight(150)
        sheet_layout.addWidget(self.text_sheet)
        
        layout.addWidget(sheet_frame)
    
    def create_status_bar(self, layout):
        self.label_status = QLabel("Ready")
        layout.addWidget(self.label_status)
        
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Space"), self, self.shortcut_play_pause)
        QShortcut(QKeySequence("Ctrl+P"), self, self.shortcut_play_pause)
        QShortcut(QKeySequence("P"), self, self.pause_clicked)
        QShortcut(QKeySequence("S"), self, self.stop_clicked)
        QShortcut(QKeySequence("Esc"), self, self.stop_clicked)
        QShortcut(QKeySequence("Ctrl+S"), self, self.stop_clicked)
    
    def setup_global_hotkeys(self):
        success = self.hotkey_manager.register(
            self.global_play_pause,
            self.global_stop
        )
        
        if not success and hasattr(self, 'label_hotkey'):
            self.label_hotkey.setText("❌ Hotkey registration failed - Run as Admin!")
            self.label_hotkey.setStyleSheet("color: #ff0000; font-weight: bold;")
    
    def shortcut_play_pause(self):
        if self.is_playing:
            self.pause_clicked()
        else:
            self.play_clicked()
    
    def global_play_pause(self):
        QTimer.singleShot(0, self._do_play_pause)
    
    def _do_play_pause(self):
        try:
            print(f"[DEBUG] _do_play_pause called - is_playing={self.is_playing}, is_paused={self.is_paused}")
            if self.is_playing:
                print("[DEBUG] Calling pause_clicked()")
                self.pause_clicked()
            else:
                print("[DEBUG] Calling play_clicked()")
                self.play_clicked()
        except Exception as e:
            print(f"❌ Error in _do_play_pause: {e}")
            import traceback
            traceback.print_exc()
    
    def global_stop(self):
        QTimer.singleShot(0, self._do_stop)
    
    def _do_stop(self):
        try:
            print("[DEBUG] _do_stop called")
            self.stop_clicked()
        except Exception as e:
            print(f"❌ Error in _do_stop: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== Theme ====================
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.dark_mode_btn.setText("🌙 Dark" if not self.dark_mode else "☀️ Light")
    
    def apply_theme(self):
        """Apply current theme"""
        self.setStyleSheet(get_theme(self.dark_mode))
    
    # ==================== MIDI File Management ====================
    
    def refresh_midi_list(self):
        self.list_midi.clear()
        midi_files = GZP.midScanner()
        if midi_files:
            self.list_midi.addItems(midi_files)
        else:
            self.list_midi.addItem("No MIDI files found")
        
        if hasattr(self, 'label_status'):
            self.label_status.setText("✓ MIDI list refreshed")
    
    def add_midi_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select MIDI File", "", "MIDI Files (*.mid *.midi);;All Files (*.*)"
        )
        
        if file_path:
            try:
                file_name = os.path.basename(file_path)
                midi_repo = "." + os.sep + "midi_repo"
                
                if not os.path.exists(midi_repo):
                    os.makedirs(midi_repo)
                
                dest_path = os.path.join(midi_repo, file_name)
                
                if os.path.exists(dest_path):
                    reply = QMessageBox.question(
                        self, "File Exists",
                        f"'{file_name}' already exists. Overwrite?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
                
                shutil.copy2(file_path, dest_path)
                self.refresh_midi_list()
                
                items = self.list_midi.findItems(file_name, Qt.MatchExactly)
                if items:
                    self.list_midi.setCurrentItem(items[0])
                    self.midi_selected(items[0])
                
                self.label_status.setText(f"✓ Added: {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add MIDI file:\n{str(e)}")
                self.label_status.setText("❌ Failed to add MIDI file")
    
    def midi_selected(self, item=None):
        try:
            if not item:
                item = self.list_midi.currentItem()
            
            if not item or item.text() == "No MIDI files found":
                self.combo_key.setEnabled(False)
                self.spin_bpm.setEnabled(False)
                self.btn_play.setEnabled(False)
                self.btn_show_sheet.setEnabled(False)
                self.btn_auto_key.setEnabled(False)
                self.label_status.setText("Ready")
                return
            
            file_name = item.text()
            print(f"[DEBUG] Selected MIDI: {file_name}")
            
            self.combo_key.clear()
            self.key_adds.clear()
            
            avail_keys = GZP.allToCMajor(file_name)
            print(f"[DEBUG] Available keys: {avail_keys}")
            
            if not avail_keys and not self.check_out_range.isChecked():
                best_key = GZP.findBestKey(file_name)
                out_notes = GZP.getOutOfRangeNotes(file_name, best_key)
                
                self.label_status.setText(
                    f"⚠️ MIDI out of range! Best key: {best_key:+d} ({len(out_notes)} notes still out). "
                    f"Enable 'Allow out-of-range' or click 'Auto' button."
                )
                
                if best_key > 0:
                    self.combo_key.addItem(f"+{best_key} key (Auto)")
                else:
                    self.combo_key.addItem(f"{best_key} key (Auto)")
                self.key_adds.append(best_key)
                
                self.combo_key.setEnabled(True)
                self.btn_auto_key.setEnabled(True)
                self.btn_play.setEnabled(False)
                self.btn_show_sheet.setEnabled(False)
                return
            
            if not avail_keys:
                avail_keys = [0]
            
            for i in avail_keys:
                if i > 0:
                    self.combo_key.addItem(f"+{i} key")
                else:
                    self.combo_key.addItem(f"{i} key")
                self.key_adds.append(i)
            
            self.combo_key.setEnabled(True)
            self.spin_bpm.setEnabled(True)
            self.btn_play.setEnabled(True)
            self.btn_show_sheet.setEnabled(True)
            self.btn_auto_key.setEnabled(True)
            
            out_notes = GZP.getOutOfRangeNotes(file_name, self.key_adds[0])
            if out_notes:
                self.label_status.setText(f"⚠️ Warning: {len(out_notes)} notes out of range")
            else:
                self.label_status.setText(f"✓ Selected: {file_name}")
                
        except Exception as e:
            print(f"❌ ERROR in midi_selected: {e}")
            import traceback
            traceback.print_exc()
            self.label_status.setText(f"❌ Error loading MIDI: {str(e)}")
    
    def auto_adjust_key(self):
        current_item = self.list_midi.currentItem()
        if not current_item:
            return
        
        file_name = current_item.text()
        best_key = GZP.findBestKey(file_name)
        out_notes = GZP.getOutOfRangeNotes(file_name, best_key)
        
        self.check_out_range.setChecked(True)
        
        self.combo_key.clear()
        self.key_adds.clear()
        
        if best_key > 0:
            self.combo_key.addItem(f"+{best_key} key (Auto-adjusted)")
        else:
            self.combo_key.addItem(f"{best_key} key (Auto-adjusted)")
        self.key_adds.append(best_key)
        
        self.btn_play.setEnabled(True)
        self.btn_show_sheet.setEnabled(True)
        self.spin_bpm.setEnabled(True)
        
        if out_notes:
            self.label_status.setText(
                f"🎯 Auto-adjusted to {best_key:+d} key. {len(out_notes)} notes will be skipped. Ready to play!"
            )
        else:
            self.label_status.setText(
                f"✓ Auto-adjusted to {best_key:+d} key. Perfect fit! Ready to play!"
            )
    
    # ==================== Playback Control ====================
    
    def play_clicked(self):
        """Start or resume playback"""
        if self.is_paused:
            self.playThread.resume()
            self.is_paused = False
            self.btn_play.setEnabled(False)
            self.btn_pause.setEnabled(True)
            self.label_status.setText("▶ Playing...")
            return
        
        wait_time = self.spin_wait.value()
        if wait_time > 0:
            self.label_status.setText(f"⏳ Starting in {wait_time}s...")
            QTimer.singleShot(wait_time * 1000, self.start_playback)
        else:
            self.start_playback()
    
    def start_playback(self):
        """Actually start playback"""
        current_item = self.list_midi.currentItem()
        if not current_item:
            self.label_status.setText("❌ No MIDI file selected")
            return
        
        file_name = current_item.text()
        key_add = self.key_adds[self.combo_key.currentIndex()]
        bpm = self.spin_bpm.value()
        allow_out = self.check_out_range.isChecked()
        
        self.playThread = PlaybackThread(file_name, key_add, bpm, allow_out)
        self.playThread.progress_signal.connect(self.update_progress)
        self.playThread.note_played_signal.connect(self.note_viz.add_note)
        self.playThread.finished_signal.connect(self.playback_finished)
        self.playThread.error_signal.connect(self.playback_error)
        
        self.playThread.start()
        
        self.is_playing = True
        self.is_paused = False
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.list_midi.setEnabled(False)
        self.combo_key.setEnabled(False)
        self.spin_wait.setEnabled(False)
        self.btn_add_midi.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self.label_status.setText("▶ Playing...")
    
    def pause_clicked(self):
        if self.playThread and self.is_playing:
            if self.is_paused:
                self.playThread.resume()
                self.is_paused = False
                self.btn_pause.setText("⏸ Pause\n(Ctrl+V)")
                self.label_status.setText("▶ Playing...")
            else:
                self.playThread.pause()
                self.is_paused = True
                self.btn_pause.setText("▶ Resume\n(Ctrl+V)")
                self.btn_play.setEnabled(True)
                self.label_status.setText("⏸ Paused")
    
    def stop_clicked(self):
        """Stop playback"""
        if self.playThread:
            self.playThread.stop()
        self.playback_finished()
    
    def playback_finished(self):
        self.is_playing = False
        self.is_paused = False
        self.btn_play.setEnabled(True)
        self.btn_play.setText("▶ Play\n(Ctrl+V)")
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("⏸ Pause\n(Ctrl+V)")
        self.btn_stop.setEnabled(False)
        self.list_midi.setEnabled(True)
        self.combo_key.setEnabled(True)
        self.spin_wait.setEnabled(True)
        self.btn_add_midi.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.progress_bar.setValue(0)
        self.label_time.setText("00:00 / 00:00")
        self.label_status.setText("✓ Playback finished")
    
    def playback_error(self, error_msg):
        self.playback_finished()
        self.label_status.setText(f"❌ Error: {error_msg}")
    
    def update_progress(self, current, total):
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            
            current_str = f"{int(current // 60):02d}:{int(current % 60):02d}"
            total_str = f"{int(total // 60):02d}:{int(total % 60):02d}"
            self.label_time.setText(f"{current_str} / {total_str}")
    
    def bpm_changed(self, value):
        if self.playThread and self.is_playing:
            self.playThread.set_bpm(value)
    
    # ==================== Sheet Music ====================
    
    def show_sheet(self):
        current_item = self.list_midi.currentItem()
        if not current_item:
            return
            
        file_name = current_item.text()
        key_add = self.key_adds[self.combo_key.currentIndex()]
        
        sheet = GSM.printMidiSheet(file_name, key_add)
        self.text_sheet.clear()
        for notes in sheet:
            self.text_sheet.append(str(notes))
        
        self.label_status.setText("✓ Sheet generated")
    
    def copy_sheet(self):
        self.text_sheet.selectAll()
        self.text_sheet.copy()
        self.label_status.setText("✓ Copied to clipboard")
    
    # ==================== Settings ====================
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.dark_mode = settings.get('dark_mode', True)
                    self.spin_bpm.setValue(settings.get('bpm', 120))
                    self.spin_wait.setValue(settings.get('wait_time', 3))
                    
                    if 'geometry' in settings:
                        self.restoreGeometry(bytes.fromhex(settings['geometry']))
        except:
            pass
    
    def save_settings(self):
        settings = {
            'dark_mode': self.dark_mode,
            'bpm': self.spin_bpm.value(),
            'wait_time': self.spin_wait.value(),
            'geometry': self.saveGeometry().toHex().data().decode()
        }
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except:
            pass
    
    def closeEvent(self, event):
        self.save_settings()
        self.hotkey_manager.unregister()
        
        if self.playThread:
            self.playThread.stop()
        event.accept()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Nishuihan Music Player")
        
        if is_admin():
            window = ModernGUI()
            window.show()
            sys.exit(app.exec_())
        else:
            if sys.version_info[0] == 3:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            else:
                ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")