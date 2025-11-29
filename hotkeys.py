"""
Global hotkey management
"""
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("Warning: 'keyboard' module not installed. Global hotkeys disabled.")
    print("Install with: pip install keyboard")


class HotkeyManager:
    """Manages global hotkeys for the application"""
    
    def __init__(self):
        self.registered = False
        self.callbacks = {}
    
    def is_available(self):
        """Check if keyboard module is available"""
        return KEYBOARD_AVAILABLE
    
    def register(self, play_pause_callback, stop_callback):
        """Register global hotkeys"""
        if not KEYBOARD_AVAILABLE:
            print("⚠️ Keyboard module not available. Global hotkeys disabled.")
            return False
        
        try:
            # Remove any existing hotkeys first
            keyboard.unhook_all()
            
            # Store callbacks
            self.callbacks['play_pause'] = play_pause_callback
            self.callbacks['stop'] = stop_callback
            
            # Ctrl+V for Play/Pause
            keyboard.add_hotkey('ctrl+v', play_pause_callback, suppress=True)
            print("✓ Registered: Ctrl+V for Play/Pause")
            
            # Ctrl+B for Stop
            keyboard.add_hotkey('ctrl+b', stop_callback, suppress=True)
            print("✓ Registered: Ctrl+B for Stop")
            
            self.registered = True
            print("✓ Global hotkeys active - works even when game is focused!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to register global hotkeys: {e}")
            print("Make sure the app is running as Administrator!")
            self.registered = False
            return False
    
    def unregister(self):
        """Unregister all hotkeys"""
        if KEYBOARD_AVAILABLE and self.registered:
            try:
                keyboard.unhook_all()
                print("✓ Global hotkeys unregistered")
                self.registered = False
            except:
                pass
    
    def is_registered(self):
        """Check if hotkeys are currently registered"""
        return self.registered