
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont


class NoteVisualization(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_notes = set()
        

        self.note_rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J'],      
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']         
        ]
        
        self.setMinimumHeight(180)
        self.setMaximumHeight(220)
        
        # Timer to fade out notes
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.fade_notes)
        self.fade_timer.start(100)
    
    def add_note(self, key):
        self.active_notes.add(key.upper())
        self.update()
        
        # Auto-remove after 500ms
        QTimer.singleShot(500, lambda: self.remove_note(key))
    
    def remove_note(self, key):
        self.active_notes.discard(key.upper())
        self.update()
    
    def fade_notes(self):
        if self.active_notes:
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Check dark mode
        dark_mode = False
        if self.parent() and hasattr(self.parent(), 'dark_mode'):
            dark_mode = self.parent().dark_mode
        
        # Background
        bg_color = QColor(20, 20, 25) if dark_mode else QColor(230, 235, 240)
        painter.fillRect(self.rect(), bg_color)
        
        # Calculate dimensions
        max_keys_per_row = 8  # Q W E R T Y U P row has 8 keys
        key_size = min((width - 40) / max_keys_per_row, 50)  # Max 50px circles
        row_height = (height - 20) / 3
        
        font = QFont("Arial", 11, QFont.Bold)
        painter.setFont(font)
        
        # Draw each row
        for row_index, row_keys in enumerate(self.note_rows):
            num_keys = len(row_keys)
            
            # Calculate centering offset for rows with fewer keys
            total_width = num_keys * key_size
            start_x = (width - total_width) / 2
            start_y = 10 + (row_index * row_height) + (row_height - key_size) / 2
            
            # Draw each key in the row
            for i, key in enumerate(row_keys):
                x = start_x + (i * key_size)
                
                # Determine color based on active state
                if key in self.active_notes:
                    # Active - bright cyan/blue glow like in game
                    fill_color = QColor(100, 200, 255, 220)
                    border_color = QColor(150, 220, 255)
                    glow = True
                else:
                    # Inactive - subtle gray
                    if dark_mode:
                        fill_color = QColor(50, 55, 65, 150)
                        border_color = QColor(80, 85, 95)
                    else:
                        fill_color = QColor(200, 205, 215, 180)
                        border_color = QColor(150, 155, 165)
                    glow = False
                
                # Draw glow effect for active keys
                if glow:
                    glow_color = QColor(100, 200, 255, 80)
                    painter.setBrush(glow_color)
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(int(x + key_size/2 - key_size*0.6), 
                                      int(start_y - key_size*0.1), 
                                      int(key_size * 1.2), 
                                      int(key_size * 1.2))
                
                # Draw key circle (like in the game)
                painter.setBrush(fill_color)
                painter.setPen(border_color)
                painter.drawEllipse(int(x + key_size * 0.1), 
                                  int(start_y), 
                                  int(key_size * 0.8), 
                                  int(key_size * 0.8))
                
                # Draw key letter
                if key in self.active_notes:
                    text_color = QColor(255, 255, 255)
                else:
                    text_color = QColor(180, 180, 180) if dark_mode else QColor(100, 100, 100)
                
                painter.setPen(text_color)
                painter.drawText(int(x), int(start_y), int(key_size), int(key_size * 0.8), 
                               Qt.AlignCenter, f"[{key}]")