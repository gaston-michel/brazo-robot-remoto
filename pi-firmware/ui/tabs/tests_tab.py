"""
Tests Tab - Predefined test routines.
Minimalistic light theme.
"""
import customtkinter as ctk

from config import PREDEFINED_TESTS
from ui.theme import (
    COLORS, ICONS,
    get_button_config, get_frame_config, get_label_config
)


class TestsTab(ctk.CTkFrame):
    """Tests tab with predefined test routine buttons."""
    
    def __init__(self, parent, robot_client):
        super().__init__(parent, fg_color="transparent")
        self.client = robot_client
        
        self._build_content()
    
    def _build_content(self):
        """Build tests content."""
        # Main card
        card = ctk.CTkFrame(self, **get_frame_config())
        card.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Header
        ctk.CTkLabel(
            card,
            text="Test Routines",
            **get_label_config("heading")
        ).pack(anchor="w", padx=16, pady=(16, 12))
        
        # Hint text
        ctk.CTkLabel(
            card,
            text="Run predefined movement patterns to verify robot operation",
            **get_label_config("muted")
        ).pack(anchor="w", padx=16, pady=(0, 12))
        
        # Test buttons
        for label, test_id in PREDEFINED_TESTS:
            self._create_test_row(card, label, test_id)
    
    def _create_test_row(self, parent, label, test_id):
        """Create a test item row."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=6)
        
        # Test info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            info_frame,
            text=f"{ICONS['axis']}  {label}",
            **get_label_config()
        ).pack(side="left")
        
        # Run button
        ctk.CTkButton(
            row,
            text=f"{ICONS['play']} Run",
            width=80,
            **get_button_config("default"),
            command=lambda tid=test_id: self._run_test(tid)
        ).pack(side="right")
    
    def _run_test(self, test_id):
        """Execute a predefined test routine."""
        self.client.run_test(test_id)
