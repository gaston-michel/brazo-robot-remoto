"""
Tests Tab - Predefined test routines.
"""
import customtkinter as ctk

from config import PREDEFINED_TESTS


class TestsTab(ctk.CTkFrame):
    """Tests tab with predefined test routine buttons."""
    
    def __init__(self, parent, robot_client):
        super().__init__(parent)
        self.client = robot_client
        
        self._build_test_buttons()
    
    def _build_test_buttons(self):
        """Build test routine buttons."""
        for label, test_id in PREDEFINED_TESTS:
            ctk.CTkButton(
                self,
                text=label,
                command=lambda tid=test_id: self._run_test(tid)
            ).pack(pady=10, padx=20, fill="x")
    
    def _run_test(self, test_id):
        """Execute a predefined test routine."""
        self.client.run_test(test_id)
