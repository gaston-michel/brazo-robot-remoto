"""
Robot Control Interface - CustomTkinter Version
Main entry point for the Raspberry Pi touch display application.
"""
import customtkinter as ctk
import threading
import time

from robot_client import RobotClient
from path_manager import PathManager


# --- Configuration ---
SERIAL_PORT = '/dev/ttyACM0'
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 320


class RobotApp(ctk.CTk):
    """Main application class for robot control interface."""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Robot Control")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        
        # For fullscreen on Raspberry Pi, uncomment:
        # self.attributes('-fullscreen', True)
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize robot client and path manager
        self.client = RobotClient(port=SERIAL_PORT)
        self.path_manager = PathManager()
        
        # Status update thread control
        self.running = True
        self.status_thread = None
        
        # Build UI
        self._create_widgets()
        
        # Start status polling
        self._start_status_polling()
        
        # Bind cleanup
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        """Create the main UI widgets."""
        # Create tabview for different screens
        self.tabview = ctk.CTkTabview(self, width=WINDOW_WIDTH-20, height=WINDOW_HEIGHT-20)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Add tabs
        self.tab_control = self.tabview.add("Control")
        self.tab_settings = self.tabview.add("Settings")
        self.tab_tests = self.tabview.add("Tests")
        self.tab_paths = self.tabview.add("Paths")
        
        # Build each tab
        self._build_control_tab()
        self._build_settings_tab()
        self._build_tests_tab()
        self._build_paths_tab()
    
    def _build_control_tab(self):
        """Build the main control tab with axis controls."""
        # Connection frame
        conn_frame = ctk.CTkFrame(self.tab_control)
        conn_frame.pack(fill="x", padx=5, pady=5)
        
        self.lbl_status = ctk.CTkLabel(conn_frame, text="Status: DISCONNECTED")
        self.lbl_status.pack(side="left", padx=10)
        
        self.btn_connect = ctk.CTkButton(conn_frame, text="Connect", width=80, 
                                          command=self._do_connect)
        self.btn_connect.pack(side="right", padx=5)
        
        self.btn_estop = ctk.CTkButton(conn_frame, text="E-STOP", width=80,
                                        fg_color="red", hover_color="darkred",
                                        command=self._do_estop)
        self.btn_estop.pack(side="right", padx=5)
        
        # Axis controls frame
        axis_frame = ctk.CTkFrame(self.tab_control)
        axis_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create axis control rows
        self.axis_labels = []
        axis_names = ["Base", "Shoulder", "Elbow", "Wrist P", "Wrist R", "Gripper"]
        
        for i, name in enumerate(axis_names):
            row_frame = ctk.CTkFrame(axis_frame)
            row_frame.pack(fill="x", pady=2)
            
            # Axis label with position
            lbl = ctk.CTkLabel(row_frame, text=f"{name}: 0.00", width=120)
            lbl.pack(side="left", padx=5)
            self.axis_labels.append(lbl)
            
            # Control buttons
            btn_minus = ctk.CTkButton(row_frame, text="-", width=40,
                                       command=lambda idx=i: self._move_axis(idx, -100))
            btn_minus.pack(side="left", padx=2)
            
            btn_plus = ctk.CTkButton(row_frame, text="+", width=40,
                                      command=lambda idx=i: self._move_axis(idx, 100))
            btn_plus.pack(side="left", padx=2)
            
            btn_home = ctk.CTkButton(row_frame, text="Home", width=60,
                                      command=lambda idx=i: self._home_axis(idx))
            btn_home.pack(side="left", padx=2)
    
    def _build_settings_tab(self):
        """Build the settings tab with speed/acceleration controls."""
        # Speed control
        speed_frame = ctk.CTkFrame(self.tab_settings)
        speed_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(speed_frame, text="Speed:").pack(side="left", padx=5)
        self.speed_slider = ctk.CTkSlider(speed_frame, from_=100, to=2000, 
                                           number_of_steps=19)
        self.speed_slider.set(1000)
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.lbl_speed = ctk.CTkLabel(speed_frame, text="1000")
        self.lbl_speed.pack(side="left", padx=5)
        
        # Acceleration control  
        accel_frame = ctk.CTkFrame(self.tab_settings)
        accel_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(accel_frame, text="Accel:").pack(side="left", padx=5)
        self.accel_slider = ctk.CTkSlider(accel_frame, from_=100, to=1000,
                                           number_of_steps=9)
        self.accel_slider.set(500)
        self.accel_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.lbl_accel = ctk.CTkLabel(accel_frame, text="500")
        self.lbl_accel.pack(side="left", padx=5)
        
        # Apply button
        btn_apply = ctk.CTkButton(self.tab_settings, text="Apply Profile",
                                   command=self._apply_profile)
        btn_apply.pack(pady=20)
        
        # Update labels on slider change
        self.speed_slider.configure(command=lambda v: self.lbl_speed.configure(text=str(int(v))))
        self.accel_slider.configure(command=lambda v: self.lbl_accel.configure(text=str(int(v))))
    
    def _build_tests_tab(self):
        """Build the tests tab with predefined test buttons."""
        tests = [
            ("Test 1: Square", 1),
            ("Test 2: Circle", 2),
            ("Test 3: Pick & Place", 3),
        ]
        
        for text, test_id in tests:
            btn = ctk.CTkButton(self.tab_tests, text=text, 
                                command=lambda tid=test_id: self._run_test(tid))
            btn.pack(pady=10, padx=20, fill="x")
    
    def _build_paths_tab(self):
        """Build the paths tab with path management."""
        # Path list
        self.path_listbox = ctk.CTkScrollableFrame(self.tab_paths, height=150)
        self.path_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self.tab_paths)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(btn_frame, text="New Path", width=80,
                      command=self._new_path).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Refresh", width=80,
                      command=self._refresh_paths).pack(side="left", padx=5)
        
        # Load initial paths
        self._refresh_paths()
    
    # --- Action Methods ---
    
    def _do_connect(self):
        """Connect/disconnect from robot."""
        if self.client.connected:
            self.client.disconnect()
            self.btn_connect.configure(text="Connect")
        else:
            if self.client.connect():
                self.btn_connect.configure(text="Disconnect")
    
    def _do_estop(self):
        """Emergency stop."""
        self.client.emergency_stop()
    
    def _move_axis(self, axis_idx, steps):
        """Move an axis by relative steps."""
        self.client.move_relative(axis_idx, steps)
    
    def _home_axis(self, axis_idx):
        """Home a specific axis."""
        self.client.home_axis(axis_idx)
    
    def _apply_profile(self):
        """Apply speed/acceleration profile."""
        speed = int(self.speed_slider.get())
        accel = int(self.accel_slider.get())
        self.client.set_profile(speed, accel)
    
    def _run_test(self, test_id):
        """Run a predefined test."""
        self.client.run_test(test_id)
    
    def _new_path(self):
        """Create a new path (placeholder - will need input dialog)."""
        # TODO: Implement path creation with CTk input dialog
        pass
    
    def _refresh_paths(self):
        """Refresh the paths list."""
        # Clear existing
        for widget in self.path_listbox.winfo_children():
            widget.destroy()
        
        # Add path buttons
        for name in self.path_manager.get_path_names():
            btn = ctk.CTkButton(self.path_listbox, text=name,
                                command=lambda n=name: self._select_path(n))
            btn.pack(fill="x", pady=2)
    
    def _select_path(self, name):
        """Select a path for viewing/running."""
        # TODO: Implement path details view
        print(f"Selected path: {name}")
    
    # --- Status Polling ---
    
    def _start_status_polling(self):
        """Start background thread for status updates."""
        self.status_thread = threading.Thread(target=self._status_loop, daemon=True)
        self.status_thread.start()
    
    def _status_loop(self):
        """Background loop to poll robot status."""
        while self.running:
            if self.client.connected:
                self.client.update_status()
                # Schedule UI update on main thread
                self.after(0, self._update_status_display)
            time.sleep(0.2)
    
    def _update_status_display(self):
        """Update UI with current robot status."""
        self.lbl_status.configure(text=f"Status: {self.client.status}")
        
        # Update axis positions
        axis_names = ["Base", "Shoulder", "Elbow", "Wrist P", "Wrist R", "Gripper"]
        for i, lbl in enumerate(self.axis_labels):
            if i < len(self.client.axes):
                lbl.configure(text=f"{axis_names[i]}: {self.client.axes[i]:.2f}")
    
    def _on_close(self):
        """Cleanup on window close."""
        self.running = False
        self.client.disconnect()
        self.destroy()


if __name__ == "__main__":
    app = RobotApp()
    app.mainloop()
