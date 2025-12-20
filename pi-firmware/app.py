"""
Robot Control Application - Main CTk Application Class.
"""
import customtkinter as ctk
import threading
import time

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    SERIAL_PORT, STATUS_POLL_INTERVAL
)
from robot_client import RobotClient
from path_manager import PathManager
from ui.tabs import ControlTab, SettingsTab, TestsTab, PathsTab


class RobotApp(ctk.CTk):
    """Main application window for robot control interface."""
    
    def __init__(self):
        super().__init__()
        
        self._configure_window()
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
        # self.attributes('-fullscreen', True)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def _init_services(self):
        """Initialize backend services."""
        self.client = RobotClient(port=SERIAL_PORT)
        self.path_manager = PathManager()
        self.running = True
    
    def _build_ui(self):
        """Build the main UI structure."""
        # Tab container
        self.tabview = ctk.CTkTabview(
            self,
            width=WINDOW_WIDTH - 20,
            height=WINDOW_HEIGHT - 20
        )
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Create tabs and embed tab content
        self._create_tabs()
    
    def _create_tabs(self):
        """Create and populate tab views."""
        # Control Tab
        tab_control = self.tabview.add("Control")
        self.control_tab = ControlTab(tab_control, self.client)
        self.control_tab.pack(fill="both", expand=True)
        
        # Settings Tab
        tab_settings = self.tabview.add("Settings")
        self.settings_tab = SettingsTab(tab_settings, self.client)
        self.settings_tab.pack(fill="both", expand=True)
        
        # Tests Tab
        tab_tests = self.tabview.add("Tests")
        self.tests_tab = TestsTab(tab_tests, self.client)
        self.tests_tab.pack(fill="both", expand=True)
        
        # Paths Tab
        tab_paths = self.tabview.add("Paths")
        self.paths_tab = PathsTab(tab_paths, self.path_manager, self.client)
        self.paths_tab.pack(fill="both", expand=True)
    
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
                # Schedule UI update on main thread
                self.after(0, self._update_ui_status)
            time.sleep(STATUS_POLL_INTERVAL)
    
    def _update_ui_status(self):
        """Update UI components with current robot status."""
        self.control_tab.update_status(
            self.client.status,
            self.client.axes
        )
    
    def _on_close(self):
        """Clean up resources on application close."""
        self.running = False
        self.client.disconnect()
        self.destroy()
