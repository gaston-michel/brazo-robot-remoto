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
    COLORS, ICONS, DIMENSIONS,
    get_button_config, get_frame_config, get_label_config, get_slider_config
)


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
        self._build_slider_row(
            card,
            label="Speed",
            min_val=MIN_SPEED,
            max_val=MAX_SPEED,
            default=DEFAULT_SPEED,
            unit="steps/s",
            slider_attr="speed_slider",
            label_attr="lbl_speed"
        )
        
        # Acceleration control
        self._build_slider_row(
            card,
            label="Acceleration",
            min_val=MIN_ACCEL,
            max_val=MAX_ACCEL,
            default=DEFAULT_ACCEL,
            unit="steps/s²",
            slider_attr="accel_slider",
            label_attr="lbl_accel"
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
    
    def _build_slider_row(self, parent, label, min_val, max_val, default, unit, slider_attr, label_attr):
        """Build a labeled slider row."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=8)
        
        # Label
        label_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
        label_frame.pack(side="left")
        label_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            label_frame,
            text=label,
            **get_label_config()
        ).pack(side="left")
        
        # Value display
        value_frame = ctk.CTkFrame(row, fg_color="transparent", width=80)
        value_frame.pack(side="right")
        value_frame.pack_propagate(False)
        
        lbl_value = ctk.CTkLabel(
            value_frame,
            text=str(default),
            **get_label_config("mono")
        )
        lbl_value.pack(side="left")
        
        ctk.CTkLabel(
            value_frame,
            text=f" {unit}",
            **get_label_config("muted")
        ).pack(side="left")
        
        setattr(self, label_attr, lbl_value)
        
        # Slider
        slider = ctk.CTkSlider(
            row,
            from_=min_val,
            to=max_val,
            number_of_steps=int((max_val - min_val) / 100),
            **get_slider_config()
        )
        slider.set(default)
        slider.pack(side="left", fill="x", expand=True, padx=16)
        
        setattr(self, slider_attr, slider)
        
        # Bind slider to label update
        slider.configure(
            command=lambda v, lbl=lbl_value: lbl.configure(text=str(int(v)))
        )
    
    def _apply_profile(self):
        """Send motion profile to robot."""
        speed = int(self.speed_slider.get())
        accel = int(self.accel_slider.get())
        self.client.set_profile(speed, accel)
