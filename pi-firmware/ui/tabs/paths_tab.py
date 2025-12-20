"""
Paths Tab - Path management interface.
"""
import customtkinter as ctk


class PathsTab(ctk.CTkFrame):
    """Paths tab for managing robot movement paths."""
    
    def __init__(self, parent, path_manager, robot_client):
        super().__init__(parent)
        self.path_manager = path_manager
        self.client = robot_client
        
        self._build_path_list()
        self._build_action_buttons()
        self.refresh_paths()
    
    def _build_path_list(self):
        """Build scrollable path list."""
        self.path_listbox = ctk.CTkScrollableFrame(self, height=150)
        self.path_listbox.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _build_action_buttons(self):
        """Build path management buttons."""
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="New Path", 
            width=80,
            command=self._create_new_path
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Refresh", 
            width=80,
            command=self.refresh_paths
        ).pack(side="left", padx=5)
    
    def refresh_paths(self):
        """Refresh the paths list from storage."""
        # Clear existing buttons
        for widget in self.path_listbox.winfo_children():
            widget.destroy()
        
        # Add button for each path
        for name in self.path_manager.get_path_names():
            ctk.CTkButton(
                self.path_listbox,
                text=name,
                command=lambda n=name: self._select_path(n)
            ).pack(fill="x", pady=2)
    
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
    
    def _select_path(self, name):
        """Handle path selection."""
        # TODO: Open path details/editing view
        print(f"Selected path: {name}")
