"""
Control Tab - Main control interface for robot axes.
Minimalistic light theme with icons.
"""
import customtkinter as ctk

from config import AXIS_NAMES, JOG_STEP_SIZE
from ui.theme import (
    COLORS, ICONS, FONTS, DIMENSIONS,
    get_button_config, get_frame_config, get_label_config
)


class ControlTab(ctk.CTkFrame):
    """Main control tab with axis controls and connection management."""
    
    def __init__(self, parent, robot_client):
        super().__init__(parent, fg_color="transparent")
        self.client = robot_client
        self.axis_labels = []
        self.axis_rows = []
        
        self._build_header()
        self._build_axis_controls()
    
    def _build_header(self):
        """Build the connection status header."""
        header = ctk.CTkFrame(self, **get_frame_config())
        header.pack(fill="x", padx=8, pady=(8, 4))
        
        # Status indicator
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.pack(side="left", padx=12, pady=10)
        
        self.status_dot = ctk.CTkLabel(
            status_frame,
            text=ICONS["disconnected"],
            font=("Segoe UI", 12),
            text_color=COLORS["text_muted"]
        )
        self.status_dot.pack(side="left", padx=(0, 6))
        
        self.lbl_status = ctk.CTkLabel(
            status_frame,
            text="Disconnected",
            **get_label_config("secondary")
        )
        self.lbl_status.pack(side="left")
        
        # Action buttons (right side)
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=8, pady=8)
        
        # E-Stop button
        self.btn_estop = ctk.CTkButton(
            btn_frame,
            text=f"{ICONS['stop']} Stop",
            width=70,
            **get_button_config("danger"),
            command=self._emergency_stop
        )
        self.btn_estop.pack(side="right", padx=(8, 0))
        
        # Connect button
        self.btn_connect = ctk.CTkButton(
            btn_frame,
            text=f"{ICONS['connect']} Connect",
            width=100,
            **get_button_config("primary"),
            command=self._toggle_connection
        )
        self.btn_connect.pack(side="right")
    
    def _build_axis_controls(self):
        """Build axis control panel."""
        # Container frame
        axes_container = ctk.CTkFrame(self, **get_frame_config())
        axes_container.pack(fill="both", expand=True, padx=8, pady=4)
        
        # Section header
        header_frame = ctk.CTkFrame(axes_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(12, 8))
        
        ctk.CTkLabel(
            header_frame,
            text="Axis Control",
            **get_label_config("heading")
        ).pack(side="left")
        
        # Axis rows
        for idx, name in enumerate(AXIS_NAMES):
            self._create_axis_row(axes_container, idx, name)
    
    def _create_axis_row(self, parent, axis_idx, axis_name):
        """Create a single axis control row."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=4)
        self.axis_rows.append(row)
        
        # Axis icon and name
        name_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
        name_frame.pack(side="left")
        name_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            name_frame,
            text=ICONS["axis"],
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=(0, 6))
        
        ctk.CTkLabel(
            name_frame,
            text=axis_name,
            **get_label_config()
        ).pack(side="left")
        
        # Position value
        lbl_pos = ctk.CTkLabel(
            row,
            text="0.00",
            width=60,
            **get_label_config("mono")
        )
        lbl_pos.pack(side="left", padx=(8, 16))
        self.axis_labels.append(lbl_pos)
        
        # Control buttons (right side)
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right")
        
        # Minus button
        ctk.CTkButton(
            btn_frame,
            text=ICONS["minus"],
            **get_button_config("icon"),
            command=lambda: self._jog_axis(axis_idx, -JOG_STEP_SIZE)
        ).pack(side="left", padx=2)
        
        # Plus button
        ctk.CTkButton(
            btn_frame,
            text=ICONS["plus"],
            **get_button_config("icon"),
            command=lambda: self._jog_axis(axis_idx, JOG_STEP_SIZE)
        ).pack(side="left", padx=2)
        
        # Home button
        ctk.CTkButton(
            btn_frame,
            text=ICONS["home"],
            **get_button_config("icon"),
            command=lambda: self._home_axis(axis_idx)
        ).pack(side="left", padx=2)
    
    # --- Actions ---
    
    def _toggle_connection(self):
        """Connect or disconnect from robot."""
        if self.client.connected:
            self.client.disconnect()
            self.btn_connect.configure(text=f"{ICONS['connect']} Connect")
            self._set_connected_state(False)
        else:
            if self.client.connect():
                self.btn_connect.configure(text=f"{ICONS['disconnect']} Disconnect")
                self._set_connected_state(True)
    
    def _set_connected_state(self, connected):
        """Update UI for connection state."""
        if connected:
            self.status_dot.configure(
                text=ICONS["connected"],
                text_color=COLORS["success"]
            )
        else:
            self.status_dot.configure(
                text=ICONS["disconnected"],
                text_color=COLORS["text_muted"]
            )
    
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
        self.lbl_status.configure(text=status)
        
        for idx, lbl in enumerate(self.axis_labels):
            if idx < len(axis_positions):
                lbl.configure(text=f"{axis_positions[idx]:.2f}")
