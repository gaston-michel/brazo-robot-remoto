"""
Settings Tab - Motion profile configuration.
"""
import customtkinter as ctk

from config import (
    DEFAULT_SPEED, DEFAULT_ACCEL,
    MIN_SPEED, MAX_SPEED,
    MIN_ACCEL, MAX_ACCEL
)


class SettingsTab(ctk.CTkFrame):
    """Settings tab for speed and acceleration configuration."""
    
    def __init__(self, parent, robot_client):
        super().__init__(parent)
        self.client = robot_client
        
        self._build_speed_control()
        self._build_accel_control()
        self._build_apply_button()
    
    def _build_speed_control(self):
        """Build speed slider control."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Speed:").pack(side="left", padx=5)
        
        self.speed_slider = ctk.CTkSlider(
            frame,
            from_=MIN_SPEED,
            to=MAX_SPEED,
            number_of_steps=19
        )
        self.speed_slider.set(DEFAULT_SPEED)
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.lbl_speed = ctk.CTkLabel(frame, text=str(DEFAULT_SPEED))
        self.lbl_speed.pack(side="left", padx=5)
        
        # Bind slider to label
        self.speed_slider.configure(
            command=lambda v: self.lbl_speed.configure(text=str(int(v)))
        )
    
    def _build_accel_control(self):
        """Build acceleration slider control."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Accel:").pack(side="left", padx=5)
        
        self.accel_slider = ctk.CTkSlider(
            frame,
            from_=MIN_ACCEL,
            to=MAX_ACCEL,
            number_of_steps=9
        )
        self.accel_slider.set(DEFAULT_ACCEL)
        self.accel_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.lbl_accel = ctk.CTkLabel(frame, text=str(DEFAULT_ACCEL))
        self.lbl_accel.pack(side="left", padx=5)
        
        # Bind slider to label
        self.accel_slider.configure(
            command=lambda v: self.lbl_accel.configure(text=str(int(v)))
        )
    
    def _build_apply_button(self):
        """Build apply profile button."""
        ctk.CTkButton(
            self,
            text="Apply Profile",
            command=self._apply_profile
        ).pack(pady=20)
    
    def _apply_profile(self):
        """Send motion profile to robot."""
        speed = int(self.speed_slider.get())
        accel = int(self.accel_slider.get())
        self.client.set_profile(speed, accel)
