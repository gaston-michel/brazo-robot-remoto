"""
UI Theme and Styling - Minimalistic Light Theme

Design principles:
- Light mode with clean whites and subtle grays
- Rounded shapes with generous corner radius
- Icons using Unicode symbols
- Limited color palette: white, black, grays, minimal accent
"""

# --- Color Palette ---
COLORS = {
    # Base colors
    "background": "#FAFAFA",      # Very light gray background
    "surface": "#FFFFFF",          # White surfaces/cards
    "surface_hover": "#F5F5F5",    # Subtle hover state
    
    # Text colors
    "text_primary": "#1A1A1A",     # Near black for main text
    "text_secondary": "#6B6B6B",   # Medium gray for secondary
    "text_muted": "#9CA3AF",       # Light gray for hints
    
    # Border colors
    "border": "#E5E5E5",           # Light border
    "border_focus": "#D1D5DB",     # Slightly darker on focus
    
    # Accent (used sparingly)
    "accent": "#6366F1",           # Indigo accent
    "accent_hover": "#4F46E5",     # Darker on hover
    
    # Status colors (used only when necessary)
    "success": "#10B981",          # Green
    "warning": "#F59E0B",          # Amber
    "danger": "#EF4444",           # Red
    "danger_hover": "#DC2626",     # Darker red
}

# --- Icons (Unicode) ---
ICONS = {
    # Navigation
    "control": "⚙",      # Gear
    "settings": "☰",     # Menu/settings
    "tests": "▶",        # Play
    "paths": "↗",        # Route/path
    
    # Actions
    "connect": "⚡",      # Connection/power
    "disconnect": "○",   # Disconnected
    "stop": "■",         # Stop
    "home": "⌂",         # Home
    "plus": "+",         # Add
    "minus": "−",        # Subtract (proper minus sign)
    "refresh": "↻",      # Refresh
    "add": "+",          # New/create
    "play": "▶",         # Play/run
    "edit": "✎",         # Edit
    "delete": "✕",       # Delete/close
    
    # Status
    "connected": "●",    # Filled circle
    "disconnected": "○", # Empty circle
    "warning": "⚠",      # Warning
    "check": "✓",        # Checkmark
    
    # Axes
    "axis": "◎",         # Target/axis
}

# --- Typography ---
FONTS = {
    "heading": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 13),
    "body_bold": ("Segoe UI", 13, "bold"),
    "small": ("Segoe UI", 11),
    "mono": ("Consolas", 12),
}

# --- Dimensions ---
DIMENSIONS = {
    "corner_radius": 12,           # Rounded corners
    "corner_radius_small": 8,      # Smaller elements
    "border_width": 1,             # Subtle borders
    "padding": 12,                 # Standard padding
    "padding_small": 8,            # Compact padding
    "button_height": 36,           # Standard button height
    "button_height_small": 28,     # Compact buttons
    "icon_button_size": 36,        # Square icon buttons
}

# --- CTk Theme Config ---
def get_button_config(style="default"):
    """Get button configuration for different styles."""
    base = {
        "corner_radius": DIMENSIONS["corner_radius_small"],
        "border_width": DIMENSIONS["border_width"],
        "height": DIMENSIONS["button_height"],
        "font": FONTS["body"],
    }
    
    styles = {
        "default": {
            **base,
            "fg_color": COLORS["surface"],
            "hover_color": COLORS["surface_hover"],
            "border_color": COLORS["border"],
            "text_color": COLORS["text_primary"],
        },
        "primary": {
            **base,
            "fg_color": COLORS["text_primary"],
            "hover_color": "#333333",
            "border_color": COLORS["text_primary"],
            "text_color": COLORS["surface"],
        },
        "accent": {
            **base,
            "fg_color": COLORS["accent"],
            "hover_color": COLORS["accent_hover"],
            "border_color": COLORS["accent"],
            "text_color": COLORS["surface"],
        },
        "danger": {
            **base,
            "fg_color": COLORS["danger"],
            "hover_color": COLORS["danger_hover"],
            "border_color": COLORS["danger"],
            "text_color": COLORS["surface"],
        },
        "ghost": {
            **base,
            "fg_color": "transparent",
            "hover_color": COLORS["surface_hover"],
            "border_color": "transparent",
            "text_color": COLORS["text_primary"],
        },
        "icon": {
            "corner_radius": DIMENSIONS["corner_radius_small"],
            "border_width": 0,
            "width": DIMENSIONS["icon_button_size"],
            "height": DIMENSIONS["icon_button_size"],
            "fg_color": "transparent",
            "hover_color": COLORS["surface_hover"],
            "text_color": COLORS["text_primary"],
            "font": ("Segoe UI", 16),
        },
    }
    
    return styles.get(style, styles["default"])


def get_frame_config():
    """Get frame configuration."""
    return {
        "corner_radius": DIMENSIONS["corner_radius"],
        "border_width": DIMENSIONS["border_width"],
        "fg_color": COLORS["surface"],
        "border_color": COLORS["border"],
    }


def get_label_config(style="default"):
    """Get label configuration."""
    styles = {
        "default": {
            "font": FONTS["body"],
            "text_color": COLORS["text_primary"],
        },
        "heading": {
            "font": FONTS["heading"],
            "text_color": COLORS["text_primary"],
        },
        "secondary": {
            "font": FONTS["body"],
            "text_color": COLORS["text_secondary"],
        },
        "muted": {
            "font": FONTS["small"],
            "text_color": COLORS["text_muted"],
        },
        "mono": {
            "font": FONTS["mono"],
            "text_color": COLORS["text_primary"],
        },
    }
    return styles.get(style, styles["default"])


def get_slider_config():
    """Get slider configuration."""
    return {
        "button_color": COLORS["text_primary"],
        "button_hover_color": "#333333",
        "progress_color": COLORS["text_primary"],
        "fg_color": COLORS["border"],
        "height": 6,
    }
