"""
Control Tab - Main control interface for robot axes.
"""
import customtkinter as ctk

from config import AXIS_NAMES, JOG_STEP_SIZE


class ControlTab(ctk.CTkFrame):
    """Main control tab with axis controls and connection management."""
    
    def __init__(self, parent, robot_client):
        super().__init__(parent)
        self.client = robot_client
        self.axis_labels = []
        
        self._build_connection_bar()
        self._build_axis_controls()
    
    def _build_connection_bar(self):
        """Build the connection status bar."""
        conn_frame = ctk.CTkFrame(self)
        conn_frame.pack(fill="x", padx=5, pady=5)
        
        self.lbl_status = ctk.CTkLabel(conn_frame, text="Status: DISCONNECTED")
        self.lbl_status.pack(side="left", padx=10)
        
        self.btn_connect = ctk.CTkButton(
            conn_frame, 
            text="Connect", 
            width=80,
            command=self._toggle_connection
        )
        self.btn_connect.pack(side="right", padx=5)
        
        self.btn_estop = ctk.CTkButton(
            conn_frame, 
            text="E-STOP", 
            width=80,
            fg_color="red", 
            hover_color="darkred",
            command=self._emergency_stop
        )
        self.btn_estop.pack(side="right", padx=5)
    
    def _build_axis_controls(self):
        """Build axis control rows."""
        axis_frame = ctk.CTkFrame(self)
        axis_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        for idx, name in enumerate(AXIS_NAMES):
            self._create_axis_row(axis_frame, idx, name)
    
    def _create_axis_row(self, parent, axis_idx, axis_name):
        """Create a single axis control row."""
        row_frame = ctk.CTkFrame(parent)
        row_frame.pack(fill="x", pady=2)
        
        # Position label
        lbl = ctk.CTkLabel(row_frame, text=f"{axis_name}: 0.00", width=120)
        lbl.pack(side="left", padx=5)
        self.axis_labels.append(lbl)
        
        # Jog buttons
        ctk.CTkButton(
            row_frame, text="-", width=40,
            command=lambda: self._jog_axis(axis_idx, -JOG_STEP_SIZE)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            row_frame, text="+", width=40,
            command=lambda: self._jog_axis(axis_idx, JOG_STEP_SIZE)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            row_frame, text="Home", width=60,
            command=lambda: self._home_axis(axis_idx)
        ).pack(side="left", padx=2)
    
    # --- Actions ---
    
    def _toggle_connection(self):
        """Connect or disconnect from robot."""
        if self.client.connected:
            self.client.disconnect()
            self.btn_connect.configure(text="Connect")
        else:
            if self.client.connect():
                self.btn_connect.configure(text="Disconnect")
    
    def _emergency_stop(self):
        """Trigger emergency stop."""
        self.client.emergency_stop()
    
    def _jog_axis(self, axis_idx, steps):
        """Jog axis by relative steps."""
        self.client.move_relative(axis_idx, steps)
    
    def _home_axis(self, axis_idx):
        """Home specific axis."""
        self.client.home_axis(axis_idx)
    
    # --- Public Methods ---
    
    def update_status(self, status, axis_positions):
        """Update display with current robot status."""
        self.lbl_status.configure(text=f"Status: {status}")
        
        for idx, lbl in enumerate(self.axis_labels):
            if idx < len(axis_positions):
                lbl.configure(text=f"{AXIS_NAMES[idx]}: {axis_positions[idx]:.2f}")
