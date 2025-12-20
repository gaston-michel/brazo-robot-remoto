"""
Paths Tab - Path management interface.
Minimalistic light theme.
"""
import customtkinter as ctk

from ui.theme import (
    COLORS, ICONS, DIMENSIONS,
    get_button_config, get_frame_config, get_label_config
)


class PathsTab(ctk.CTkFrame):
    """Paths tab for managing robot movement paths."""
    
    def __init__(self, parent, path_manager, robot_client):
        super().__init__(parent, fg_color="transparent")
        self.path_manager = path_manager
        self.client = robot_client
        
        self._build_content()
        self.refresh_paths()
    
    def _build_content(self):
        """Build paths content."""
        # Main card
        card = ctk.CTkFrame(self, **get_frame_config())
        card.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Header with actions
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 12))
        
        ctk.CTkLabel(
            header,
            text="Saved Paths",
            **get_label_config("heading")
        ).pack(side="left")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(
            btn_frame,
            text=ICONS["refresh"],
            **get_button_config("icon"),
            command=self.refresh_paths
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text=f"{ICONS['add']} New",
            width=70,
            **get_button_config("primary"),
            command=self._create_new_path
        ).pack(side="left", padx=(8, 0))
        
        # Path list container
        self.path_list = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent",
            height=180
        )
        self.path_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        # Empty state (shown when no paths)
        self.empty_label = ctk.CTkLabel(
            self.path_list,
            text="No saved paths yet",
            **get_label_config("muted")
        )
    
    def refresh_paths(self):
        """Refresh the paths list from storage."""
        # Clear existing items
        for widget in self.path_list.winfo_children():
            if widget != self.empty_label:
                widget.destroy()
        
        paths = self.path_manager.get_path_names()
        
        if not paths:
            self.empty_label.pack(pady=20)
        else:
            self.empty_label.pack_forget()
            for name in paths:
                self._create_path_row(name)
    
    def _create_path_row(self, name):
        """Create a path list item."""
        row = ctk.CTkFrame(
            self.path_list,
            fg_color=COLORS["surface_hover"],
            corner_radius=DIMENSIONS["corner_radius_small"]
        )
        row.pack(fill="x", pady=4, padx=4)
        
        # Path icon and name
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=12, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=ICONS["paths"],
            font=("Segoe UI", 12),
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            info_frame,
            text=name,
            **get_label_config()
        ).pack(side="left")
        
        # Point count (if available)
        points = self.path_manager.get_path(name)
        if points:
            ctk.CTkLabel(
                info_frame,
                text=f"  •  {len(points)} points",
                **get_label_config("muted")
            ).pack(side="left")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=4)
        
        ctk.CTkButton(
            btn_frame,
            text=ICONS["play"],
            **get_button_config("icon"),
            command=lambda n=name: self._run_path(n)
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text=ICONS["delete"],
            **get_button_config("icon"),
            command=lambda n=name: self._delete_path(n)
        ).pack(side="left")
    
    def _create_new_path(self):
        """Open dialog to create a new path."""
        dialog = ctk.CTkInputDialog(
            text="Enter path name:",
            title="New Path"
        )
        name = dialog.get_input()
        
        if name and name.strip():
            self.path_manager.add_path(name.strip())
            self.refresh_paths()
    
    def _run_path(self, name):
        """Run a saved path."""
        # TODO: Implement path execution
        print(f"Running path: {name}")
    
    def _delete_path(self, name):
        """Delete a path after confirmation."""
        self.path_manager.delete_path(name)
        self.refresh_paths()
