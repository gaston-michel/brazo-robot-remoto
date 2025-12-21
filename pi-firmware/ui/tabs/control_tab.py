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
from ui.components import ConnectionSelector
from ui.components.axis_slider import AxisSlider


class ControlTab(ctk.CTkFrame):
    """Main control tab with axis controls and connection management."""
    
    def __init__(self, parent, robot_client):
        super().__init__(parent, fg_color="transparent")
        self.client = robot_client
        self.axis_sliders = []  # AxisSlider components
        self.axis_rows = []
        
        self._build_header()
        self._build_axis_controls()
    
    def _build_header(self):
        """Build the header with connection selector and E-Stop."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=6, pady=(4, 2))
        
        # Connection selector (left side) - no expand, auto width
        self.connection_selector = ConnectionSelector(
            header,
            self.client,
            on_connection_change=self._on_connection_change
        )
        self.connection_selector.pack(side="left")
        
        # E-Stop button (right side) - compact size
        self.btn_estop = ctk.CTkButton(
            header,
            text=f"{ICONS['stop']} STOP",
            width=55,
            height=30,
            corner_radius=DIMENSIONS["corner_radius_small"],
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            text_color=COLORS["surface"],
            font=("Segoe UI Semibold", 10),  # Bold
            command=self._emergency_stop
        )
        self.btn_estop.pack(side="right", padx=(4, 0))
    
    def _build_axis_controls(self):
        """Build axis control panel."""
        # Container frame
        axes_container = ctk.CTkFrame(
            self, 
            fg_color=COLORS["surface"],
            corner_radius=DIMENSIONS["corner_radius"],
            border_width=1,
            border_color=COLORS["border"]
        )
        axes_container.pack(fill="both", expand=True, padx=6, pady=2)
        
        # Configure grid rows to be equal weight
        for i in range(len(AXIS_NAMES)):
            axes_container.grid_rowconfigure(i, weight=1)
        axes_container.grid_columnconfigure(0, weight=1)
        
        # Axis rows using grid
        for idx, name in enumerate(AXIS_NAMES):
            self._create_axis_row(axes_container, idx, name)
    
    def _create_axis_row(self, parent, axis_idx, axis_name):
        """Create a single axis control row."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=axis_idx, column=0, sticky="ew", padx=12, pady=2)
        self.axis_rows.append(row)
        
        # Axis name (bold, no icon)
        name_frame = ctk.CTkFrame(row, fg_color="transparent", width=90)
        name_frame.pack(side="left")
        name_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            name_frame,
            text=axis_name,
            font=FONTS["body_medium"],
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
        
        # Position slider (replaces simple label)
        slider = AxisSlider(
            row,
            max_value=360,
            on_value_change=lambda v, idx=axis_idx: self._on_slider_change(idx, v)
        )
        slider.pack(side="left", fill="x", expand=True, padx=(8, 8))
        self.axis_sliders.append(slider)
        
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
    
    def _on_connection_change(self, connected):
        """Handle connection state changes from the selector."""
        # Could add additional logic here if needed
        pass
    
    def _on_slider_change(self, axis_idx, value):
        """Handle slider value change."""
        # Move axis to the slider position
        self.client.move_absolute(axis_idx, value)
    
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
        # Update connection selector status
        if hasattr(self, 'connection_selector'):
            self.connection_selector.update_status(status)
        
        # Update axis sliders with positions
        for idx, slider in enumerate(self.axis_sliders):
            if idx < len(axis_positions):
                slider.set_value(axis_positions[idx])

