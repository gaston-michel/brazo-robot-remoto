"""
Custom Axis Slider - Visual slider with value display for robot axes.
"""
import customtkinter as ctk
import tkinter as tk
from ui.theme import COLORS, FONTS, DIMENSIONS


class AxisSlider(ctk.CTkFrame):
    """Custom slider showing current value and max value with sliding thumb."""
    
    def __init__(self, parent, max_value=360, on_value_change=None):
        super().__init__(
            parent,
            fg_color=COLORS["surface_hover"],  # Light gray track
            corner_radius=DIMENSIONS["corner_radius"],
            height=32
        )
        
        self.max_value = max_value
        self.current_value = 0
        self.on_value_change = on_value_change
        
        self._build_ui()
        self._update_display()
    
    def _build_ui(self):
        """Build the slider UI."""
        # Max value label (positioned away from edges to preserve rounded corners)
        self.lbl_max = tk.Label(
            self,
            text=f"{self.max_value}°",
            font=("Segoe UI", 11),
            fg=COLORS["text_muted"],
            bg=COLORS["surface_hover"],  # Match track
            anchor="center"
        )
        self.lbl_max.place(relx=0.9, rely=0.5, anchor="center")
        
        # Thumb (white rounded rectangle showing current position)
        self.thumb = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            bg_color="transparent",  # Prevent corner artifacts
            corner_radius=DIMENSIONS["corner_radius"] - 2,
            border_width=1,
            border_color=COLORS["border"]
        )
        
        # Grip indicator inside thumb
        self.lbl_grip = tk.Label(
            self.thumb,
            text="| |",
            font=("Segoe UI", 8),
            fg=COLORS["border"],
            bg=COLORS["surface"]
        )
        self.lbl_grip.pack(side="right", padx=(0, 8), pady=4)
        
        # Place thumb with small offset to stay within rounded corners
        self.thumb.place(x=3, rely=0.5, anchor="w", relwidth=0.35, relheight=0.8)
        
        # Current value label - placed ON the track, follows thumb
        self.lbl_current = tk.Label(
            self,
            text="0°",
            font=("Segoe UI Semibold", 11),
            fg=COLORS["text_primary"],
            bg=COLORS["surface"]  # Match thumb (white)
        )
        self.lbl_current.place(x=10, rely=0.5, anchor="w")
        self.lbl_current.lift()  # Ensure label is above thumb
        
        # Bind for dragging and clicking
        self.thumb.bind("<B1-Motion>", self._on_drag)
        self.thumb.bind("<Button-1>", self._on_click)
        self.lbl_current.bind("<B1-Motion>", self._on_drag_from_label)
        self.lbl_current.bind("<Button-1>", self._on_click)
        self.lbl_grip.bind("<B1-Motion>", self._on_drag_from_label)
        self.lbl_grip.bind("<Button-1>", self._on_click)
        self.bind("<Button-1>", self._on_track_click)
    
    def _update_display(self):
        """Update the visual display based on current value."""
        # Calculate thumb width (min 5%, max 97%)
        percentage = self.current_value / self.max_value if self.max_value > 0 else 0
        thumb_width = 0.15 + (percentage * 0.97)
        thumb_width = max(0.15, min(0.97, thumb_width))
        
        # Update thumb size
        self.thumb.place_configure(relwidth=thumb_width)
        
        # Update value text
        self.lbl_current.configure(text=f"{self.current_value:.1f}°")
    
    def set_value(self, value):
        """Set the current value."""
        self.current_value = max(0, min(self.max_value, value))
        self._update_display()
    
    def get_value(self):
        """Get the current value."""
        return self.current_value
    
    def _on_drag(self, event):
        """Handle thumb drag."""
        widget_x = self.thumb.winfo_x() + event.x
        self._update_from_position(widget_x)
    
    def _on_drag_from_label(self, event):
        """Handle drag from label inside thumb."""
        # Get position relative to thumb, then to slider
        label_x = event.widget.winfo_x()
        widget_x = self.thumb.winfo_x() + label_x + event.x
        self._update_from_position(widget_x)
    
    def _update_from_position(self, widget_x):
        """Update value from x position."""
        track_width = self.winfo_width()
        if track_width > 0:
            percentage = min(1.0, max(0, widget_x / track_width))
            new_value = percentage * self.max_value
            self.set_value(new_value)
            
            if self.on_value_change:
                self.on_value_change(self.current_value)
    
    def _on_click(self, event):
        """Handle thumb click."""
        pass  # Just for starting drag
    
    def _on_track_click(self, event):
        """Handle click on track to jump to position."""
        track_width = self.winfo_width()
        if track_width > 0:
            percentage = min(1.0, max(0, event.x / track_width))
            new_value = percentage * self.max_value
            self.set_value(new_value)
            
            if self.on_value_change:
                self.on_value_change(self.current_value)
