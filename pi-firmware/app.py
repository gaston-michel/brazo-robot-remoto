"""
Robot Control Application - Main CTk Application Class.
Minimalistic light theme with icon tabs.
"""
import customtkinter as ctk
import threading
import time
import os

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    SERIAL_PORT, STATUS_POLL_INTERVAL
)
from robot_client import RobotClient
from path_manager import PathManager
from ui.theme import COLORS
from ui.components import IconTabBar
from ui.tabs import ControlTab, SettingsTab, TestsTab, PathsTab


# Icon paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons")


class RobotApp(ctk.CTk):
    """Main application window for robot control interface."""
    
    def __init__(self):
        super().__init__()
        
        self._configure_window()
        self._configure_theme()
        self._init_services()
        self._build_ui()
        self._start_background_tasks()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _configure_window(self):
        """Configure main window properties."""
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        
        
        # Uncomment for fullscreen on Raspberry Pi:
        self.attributes('-fullscreen', True)
    
    def _configure_theme(self):
        """Configure CTk appearance for light minimalistic theme."""
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLORS["background"])
    
    def _init_services(self):
        """Initialize backend services."""
        self.client = RobotClient(port=SERIAL_PORT)
        self.path_manager = PathManager()
        self.running = True
    
    def _build_ui(self):
        """Build the main UI structure."""
        # Define tabs with icons
        tabs = [
            ("Control", os.path.join(ASSETS_DIR, "control.png"), self._build_control_tab),
            ("Settings", os.path.join(ASSETS_DIR, "settings.png"), self._build_settings_tab),
            ("Tests", os.path.join(ASSETS_DIR, "tests.png"), self._build_tests_tab),
            ("Paths", os.path.join(ASSETS_DIR, "paths.png"), self._build_paths_tab),
        ]
        
        # Create custom icon tab bar
        self.tab_bar = IconTabBar(self, tabs)
        self.tab_bar.pack(fill="both", expand=True, padx=2, pady=2)
    
    def _build_control_tab(self, parent):
        """Build control tab content."""
        self.control_tab = ControlTab(parent, self.client)
        return self.control_tab
    
    def _build_settings_tab(self, parent):
        """Build settings tab content."""
        self.settings_tab = SettingsTab(parent, self.client)
        return self.settings_tab
    
    def _build_tests_tab(self, parent):
        """Build tests tab content."""
        self.tests_tab = TestsTab(parent, self.client)
        return self.tests_tab
    
    def _build_paths_tab(self, parent):
        """Build paths tab content."""
        self.paths_tab = PathsTab(parent, self.path_manager, self.client)
        return self.paths_tab
    
    def _start_background_tasks(self):
        """Start background worker threads."""
        self.status_thread = threading.Thread(
            target=self._status_polling_loop,
            daemon=True
        )
        self.status_thread.start()
    
    def _status_polling_loop(self):
        """Background loop for polling robot status."""
        while self.running:
            if self.client.connected:
                self.client.update_status()
                self.after(0, self._update_ui_status)
            time.sleep(STATUS_POLL_INTERVAL)
    
    def _update_ui_status(self):
        """Update UI components with current robot status."""
        if hasattr(self, 'control_tab'):
            self.control_tab.update_status(
                self.client.status,
                self.client.axes
            )
    
    def _on_close(self):
        """Clean up resources on application close."""
        self.running = False
        self.client.disconnect()
        self.destroy()
