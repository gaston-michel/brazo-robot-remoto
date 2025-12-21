"""
Custom Tab Bar - Tab navigation with image icons.
"""
import customtkinter as ctk
from PIL import Image
import os

from ui.theme import COLORS, FONTS


class IconTabBar(ctk.CTkFrame):
    """Custom tab bar with image icons and text labels."""
    
    def __init__(self, parent, tabs, on_tab_change=None):
        """
        Initialize the icon tab bar.
        
        Args:
            parent: Parent widget
            tabs: List of tuples (name, icon_path, content_builder_func)
            on_tab_change: Callback when tab changes
        """
        super().__init__(parent, fg_color=COLORS["background"])
        
        self.tabs = tabs
        self.on_tab_change = on_tab_change
        self.buttons = []
        self.current_tab = 0
        self.content_frames = {}
        
        self._build_tab_bar()
        self._build_content_area()
        
        # Select first tab
        self._select_tab(0)
    
    def _build_tab_bar(self):
        """Build the tab button bar."""
        self.tab_bar = ctk.CTkFrame(self, fg_color=COLORS["background"], height=40)
        self.tab_bar.pack(fill="x", padx=8, pady=(4, 0))
        self.tab_bar.pack_propagate(False)
        
        # Center the buttons
        button_container = ctk.CTkFrame(self.tab_bar, fg_color=COLORS["background"])
        button_container.pack(expand=True)
        
        for idx, (name, icon_path, _) in enumerate(self.tabs):
            btn = self._create_tab_button(button_container, idx, name, icon_path)
            btn.pack(side="left", padx=4)
            self.buttons.append(btn)
    
    def _create_tab_button(self, parent, index, name, icon_path):
        """Create a single tab button with icon and text."""
        # Load icon
        icon_image = None
        if icon_path and os.path.exists(icon_path):
            try:
                pil_image = Image.open(icon_path)
                # Resize to appropriate size
                icon_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(16, 16)
                )
            except Exception as e:
                print(f"Error loading icon {icon_path}: {e}")
        
        btn = ctk.CTkButton(
            parent,
            text=name,
            image=icon_image,
            compound="left",  # Icon on left of text
            width=90,
            height=32,
            corner_radius=16,  # Pill shape
            border_width=0,
            font=FONTS["tab"],
            # Default unselected style
            fg_color=COLORS["background"],
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_muted"],
            command=lambda i=index: self._select_tab(i)
        )
        
        return btn
    
    def _build_content_area(self):
        """Build the content area for tab contents."""
        self.content_area = ctk.CTkFrame(self, fg_color=COLORS["background"])
        self.content_area.pack(fill="both", expand=True)
    
    def _select_tab(self, index):
        """Select a tab by index."""
        # Update button styles
        for i, btn in enumerate(self.buttons):
            if i == index:
                # Selected style: white pill, dark text
                btn.configure(
                    fg_color=COLORS["surface"],
                    text_color=COLORS["text_primary"]
                )
            else:
                # Unselected style: no bg, gray text
                btn.configure(
                    fg_color=COLORS["background"],
                    text_color=COLORS["text_muted"]
                )
        
        # Hide all content frames
        for frame in self.content_frames.values():
            frame.pack_forget()
        
        # Show or create the selected content
        if index not in self.content_frames:
            # Create content frame using the builder function
            _, _, builder_func = self.tabs[index]
            frame = ctk.CTkFrame(self.content_area, fg_color=COLORS["background"])
            content = builder_func(frame)
            if content:
                content.pack(fill="both", expand=True)
            self.content_frames[index] = frame
        
        self.content_frames[index].pack(fill="both", expand=True)
        self.current_tab = index
        
        # Callback
        if self.on_tab_change:
            self.on_tab_change(index, self.tabs[index][0])
    
    def get_current_tab(self):
        """Get the current tab index."""
        return self.current_tab
    
    def get_content_frame(self, index):
        """Get the content frame for a specific tab."""
        return self.content_frames.get(index)
