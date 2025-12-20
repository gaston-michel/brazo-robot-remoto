"""
Robot Control Interface - Entry Point

Usage:
    python main.py
"""
from app import RobotApp


def main():
    """Application entry point."""
    app = RobotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
