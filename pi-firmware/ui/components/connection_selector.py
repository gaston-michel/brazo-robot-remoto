"""
Connection Selector - Dropdown component for serial port connection.
"""
import customtkinter as ctk
import serial.tools.list_ports
import os
from PIL import Image

from ui.theme import COLORS, FONTS, DIMENSIONS, get_frame_config

# Icon paths
ICONS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons")
ARROW_ICON_PATH = os.path.join(ICONS_DIR, "arrow_down.png")
USB_ICON_PATH = os.path.join(ICONS_DIR, "usb.png")


class ConnectionSelector(ctk.CTkFrame):
    """Dropdown selector for serial port connection with status display."""
    
    def __init__(self, parent, robot_client, on_connection_change=None):
        super().__init__(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=DIMENSIONS["corner_radius"],
            border_width=1,
            border_color=COLORS["border"]
        )
        
        self.client = robot_client
        self.on_connection_change = on_connection_change
        self.dropdown_visible = False
        self.dropdown_frame = None
        
        self._build_ui()
        self._update_display()
    
    def _build_ui(self):
        """Build the main selector content."""
        # Make the entire frame clickable
        self.bind("<Button-1>", lambda e: self._toggle_dropdown())
        
        # Content container - minimal padding
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=6, pady=3)
        content.bind("<Button-1>", lambda e: self._toggle_dropdown())
        
        # USB icon on the left
        self.usb_image = None
        if os.path.exists(USB_ICON_PATH):
            try:
                pil_image = Image.open(USB_ICON_PATH)
                self.usb_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(16, 16)
                )
            except Exception as e:
                print(f"Error loading USB icon: {e}")
        
        if self.usb_image:
            self.usb_label = ctk.CTkLabel(
                content,
                text="",
                image=self.usb_image,
                width=18
            )
            self.usb_label.pack(side="left", padx=(0, 6))
            self.usb_label.bind("<Button-1>", lambda e: self._toggle_dropdown())
        
        # Text container
        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.pack(side="left", fill="y")
        text_frame.bind("<Button-1>", lambda e: self._toggle_dropdown())
        
        # Port label (primary - bold, top)
        self.lbl_port = ctk.CTkLabel(
            text_frame,
            text="No port selected",
            font=("Segoe UI Semibold", 10),  # Small but bold
            text_color=COLORS["text_primary"],
            anchor="w",
            height=14
        )
        self.lbl_port.pack(anchor="w")
        self.lbl_port.bind("<Button-1>", lambda e: self._toggle_dropdown())
        
        # Status label (secondary - below) - explicit small height
        self.lbl_status = ctk.CTkLabel(
            text_frame,
            text="Disconnected",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="w",
            height=14
        )
        self.lbl_status.pack(anchor="w")
        self.lbl_status.bind("<Button-1>", lambda e: self._toggle_dropdown())
        
        # Dropdown arrow icon
        self.arrow_image = None
        if os.path.exists(ARROW_ICON_PATH):
            try:
                pil_image = Image.open(ARROW_ICON_PATH)
                self.arrow_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(12, 12)
                )
            except Exception as e:
                print(f"Error loading arrow icon: {e}")
        
        self.arrow_label = ctk.CTkLabel(
            content,
            text="" if self.arrow_image else "▼",
            image=self.arrow_image,
            width=14
        )
        self.arrow_label.pack(side="left", padx=(12, 0))
        self.arrow_label.bind("<Button-1>", lambda e: self._toggle_dropdown())
        
        # Hover effect
        self.bind("<Enter>", lambda e: self.configure(fg_color=COLORS["surface_hover"]))
        self.bind("<Leave>", lambda e: self.configure(fg_color=COLORS["surface"]))
    
    def _toggle_dropdown(self):
        """Toggle the dropdown menu visibility."""
        if self.dropdown_visible:
            self._hide_dropdown()
        else:
            self._show_dropdown()
    
    def _show_dropdown(self):
        """Show the dropdown menu with available ports."""
        if self.dropdown_frame:
            self._hide_dropdown()
        
        self.update_idletasks()
        dropdown_width = max(self.winfo_width(), 200)
        
        toplevel = self.winfo_toplevel()
        
        # Create dropdown frame in toplevel for proper z-order
        self.dropdown_frame = ctk.CTkFrame(
            toplevel,
            width=dropdown_width,
            fg_color=COLORS["surface"],
            bg_color="transparent",  # Fix corner artifacts
            corner_radius=DIMENSIONS["corner_radius"],
            border_width=1,
            border_color=COLORS["border"]
        )
        
        # Calculate position - adjust for title bar and padding
        x = self.winfo_rootx() - toplevel.winfo_rootx() - 6  # Align left
        y = self.winfo_rooty() - toplevel.winfo_rooty() + self.winfo_height() - 36
        
        self.dropdown_frame.place(x=x, y=y)
        self.dropdown_frame.lift()  # Bring to front
        
        # Scan for available ports
        ports = self._scan_ports()
        
        if self.client.connected:
            # Show disconnect option first
            self._add_dropdown_item(
                f"⚡ Disconnect",
                self._disconnect,
                is_action=True
            )
            
            # Divider
            divider = ctk.CTkFrame(
                self.dropdown_frame,
                fg_color=COLORS["border"],
                height=1
            )
            divider.pack(fill="x", padx=8, pady=4)
        
        if ports:
            # Show available ports
            for port, desc in ports:
                # Skip currently connected port
                if self.client.connected and port == self.client.port:
                    continue
                self._add_dropdown_item(
                    f"{port}",
                    lambda p=port: self._connect_to_port(p),
                    subtitle=desc
                )
        else:
            # No ports available
            no_ports = ctk.CTkLabel(
                self.dropdown_frame,
                text="No ports available",
                font=FONTS["small"],
                text_color=COLORS["text_muted"]
            )
            no_ports.pack(pady=12)
        
        # Refresh option
        divider = ctk.CTkFrame(
            self.dropdown_frame,
            fg_color=COLORS["border"],
            height=1
        )
        divider.pack(fill="x", padx=8, pady=4)
        
        self._add_dropdown_item(
            "↻ Refresh ports",
            self._refresh_dropdown,
            is_action=True
        )
        
        self.dropdown_visible = True
        # Arrow stays the same (image doesn't change)
        
        # Bind click outside to close
        self.winfo_toplevel().bind("<Button-1>", self._on_click_outside, add="+")
    
    def _add_dropdown_item(self, text, command, subtitle=None, is_action=False):
        """Add an item to the dropdown menu."""
        item_frame = ctk.CTkFrame(
            self.dropdown_frame,
            fg_color="transparent",
            corner_radius=DIMENSIONS["corner_radius_small"]
        )
        item_frame.pack(fill="x", padx=4, pady=2)
        
        # Bind click
        item_frame.bind("<Button-1>", lambda e: self._on_item_click(command))
        item_frame.bind("<Enter>", lambda e: item_frame.configure(fg_color=COLORS["surface_hover"]))
        item_frame.bind("<Leave>", lambda e: item_frame.configure(fg_color="transparent"))
        
        # Content padding
        content = ctk.CTkFrame(item_frame, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=6)
        content.bind("<Button-1>", lambda e: self._on_item_click(command))
        
        # Main text
        lbl = ctk.CTkLabel(
            content,
            text=text,
            font=FONTS["body"] if not is_action else FONTS["small"],
            text_color=COLORS["text_primary"] if not is_action else COLORS["text_secondary"],
            anchor="w"
        )
        lbl.pack(anchor="w")
        lbl.bind("<Button-1>", lambda e: self._on_item_click(command))
        
        # Subtitle if provided
        if subtitle:
            display_text = subtitle[:35] + "..." if len(subtitle) > 35 else subtitle
            sub_lbl = ctk.CTkLabel(
                content,
                text=display_text,
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
                anchor="w"
            )
            sub_lbl.pack(anchor="w")
            sub_lbl.bind("<Button-1>", lambda e: self._on_item_click(command))
    
    def _on_item_click(self, command):
        """Handle dropdown item click."""
        self._hide_dropdown()
        command()
    
    def _hide_dropdown(self):
        """Hide the dropdown menu."""
        if self.dropdown_frame:
            self.dropdown_frame.destroy()
            self.dropdown_frame = None
        self.dropdown_visible = False
        # Arrow stays the same (image doesn't change)
        
        # Unbind click outside
        try:
            self.winfo_toplevel().unbind("<Button-1>")
        except:
            pass
    
    def _on_click_outside(self, event):
        """Handle click outside dropdown to close it."""
        if self.dropdown_frame:
            # Check if click is outside dropdown
            x, y = event.x_root, event.y_root
            dx = self.dropdown_frame.winfo_rootx()
            dy = self.dropdown_frame.winfo_rooty()
            dw = self.dropdown_frame.winfo_width()
            dh = self.dropdown_frame.winfo_height()
            
            # Also check if click is on the selector itself
            sx = self.winfo_rootx()
            sy = self.winfo_rooty()
            sw = self.winfo_width()
            sh = self.winfo_height()
            
            in_dropdown = dx <= x <= dx + dw and dy <= y <= dy + dh
            in_selector = sx <= x <= sx + sw and sy <= y <= sy + sh
            
            if not in_dropdown and not in_selector:
                self._hide_dropdown()
    
    def _scan_ports(self):
        """Scan for available serial ports."""
        try:
            ports = serial.tools.list_ports.comports()
            return [(p.device, p.description) for p in ports]
        except:
            return []
    
    def _connect_to_port(self, port):
        """Connect to a specific port."""
        # Disconnect first if connected
        if self.client.connected:
            self.client.disconnect()
        
        # Update port and connect
        self.client.port = port
        success = self.client.connect()
        
        self._update_display()
        
        if self.on_connection_change:
            self.on_connection_change(success)
    
    def _disconnect(self):
        """Disconnect from current port."""
        self.client.disconnect()
        self._update_display()
        
        if self.on_connection_change:
            self.on_connection_change(False)
    
    def _refresh_dropdown(self):
        """Refresh the dropdown with updated port list."""
        self._show_dropdown()
    
    def _update_display(self):
        """Update the display based on connection status."""
        # Soft desaturated red for disconnected state
        DISCONNECTED_RED = "#B88888"
        
        if self.client.connected:
            # Connected: bold dark port, green status
            self.lbl_port.configure(
                text=self.client.port,
                text_color=COLORS["text_primary"]
            )
            self.lbl_status.configure(
                text="Connected",
                text_color=COLORS["success"]
            )
        else:
            # Disconnected: soft red styling
            self.lbl_port.configure(
                text="No port selected",
                text_color=DISCONNECTED_RED
            )
            self.lbl_status.configure(
                text="Click to connect",
                text_color=COLORS["text_muted"]
            )
    
    def update_status(self, status):
        """Update status from external source."""
        if self.client.connected:
            self.lbl_status.configure(text=status)
