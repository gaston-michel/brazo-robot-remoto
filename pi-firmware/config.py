"""
Application configuration constants.
"""

# Serial Communication
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

# Window Settings
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 320
WINDOW_TITLE = "Robot Control"

# Robot Axes Configuration
AXIS_NAMES = ["Base", "Shoulder", "Elbow", "Wrist P", "Wrist R", "Gripper"]
AXIS_COUNT = 6

# Motion Defaults
DEFAULT_SPEED = 1000
DEFAULT_ACCEL = 500
MIN_SPEED = 100
MAX_SPEED = 2000
MIN_ACCEL = 100
MAX_ACCEL = 1000

# Step size for jog buttons
JOG_STEP_SIZE = 100

# Status polling interval (seconds)
STATUS_POLL_INTERVAL = 0.2

# Predefined Tests
PREDEFINED_TESTS = [
    ("Test 1: Square", 1),
    ("Test 2: Circle", 2),
    ("Test 3: Pick & Place", 3),
]
