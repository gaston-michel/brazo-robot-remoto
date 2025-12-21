"""
Settings Tab - Motion profile configuration.
Minimalistic light theme.
"""
import customtkinter as ctk

from config import (
    DEFAULT_SPEED, DEFAULT_ACCEL,
    MIN_SPEED, MAX_SPEED,
    MIN_ACCEL, MAX_ACCEL
)
from ui.theme import (
    COLORS, ICONS, DIMENSIONS, FONTS,
    get_button_config, get_frame_config, get_label_config
)
from ui.components.axis_slider import AxisSlider


class SettingsTab(ctk.CTkFrame):
    """Settings tab for speed and acceleration configuration."""
    
    def __init__(self, parent, robot_client):
        super().__init__(parent, fg_color="transparent")
        self.client = robot_client
        
        self._build_content()
    
    def _build_content(self):
        """Build settings content."""
        # Main card
        card = ctk.CTkFrame(self, **get_frame_config())
        card.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Header
        ctk.CTkLabel(
            card,
            text="Motion Profile",
            **get_label_config("heading")
        ).pack(anchor="w", padx=16, pady=(16, 12))
        
        # Speed control
        self._build_setting_row(
            card,
            label="Speed",
            min_val=MIN_SPEED,
            max_val=MAX_SPEED,
            default=DEFAULT_SPEED,
            unit="/s",
            step=100,
            attr_name="speed_slider"
        )
        
        # Acceleration control
        self._build_setting_row(
            card,
            label="Acceleration",
            min_val=MIN_ACCEL,
            max_val=MAX_ACCEL,
            default=DEFAULT_ACCEL,
            unit="/s²",
            step=100,
            attr_name="accel_slider"
        )
        
        # Spacer
        ctk.CTkFrame(card, fg_color="transparent", height=16).pack()
        
        # Apply button
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(8, 16))
        
        ctk.CTkButton(
            btn_frame,
            text=f"{ICONS['check']} Apply",
            width=120,
            **get_button_config("primary"),
            command=self._apply_profile
        ).pack(side="right")
    
    def _build_setting_row(self, parent, label, min_val, max_val, default, unit, step, attr_name):
        """Build a setting row with AxisSlider."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=8)
        
        # Label (Bold)
        ctk.CTkLabel(
            row,
            text=label,
            font=FONTS["body_medium"],  # Bold font
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 4))
        
        # Slider
        slider = AxisSlider(
            row,
            min_value=min_val,
            max_value=max_val,
            unit=unit,
            step=step
        )
        slider.set_value(default)
        slider.pack(fill="x")
        
        setattr(self, attr_name, slider)
    
    def _apply_profile(self):
        """Send motion profile to robot."""
        # Getting value from AxisSlider
        speed = int(self.speed_slider.get_value())
        accel = int(self.accel_slider.get_value())
        self.client.set_profile(speed, accel)
