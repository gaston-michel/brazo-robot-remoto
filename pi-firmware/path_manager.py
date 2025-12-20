"""
Path Manager - Handles saving and loading robot movement paths.
Migrated from feature/lcd-kernel-driver branch.
"""
import json
import os


class PathManager:
    def __init__(self, filename="paths.json"):
        self.filename = filename
        self.paths = {}
        self.load()

    def load(self):
        """Load paths from JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.paths = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading paths: {e}")
                self.paths = {}
        else:
            self.paths = {}

    def save(self):
        """Save paths to JSON file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.paths, f, indent=2)
        except IOError as e:
            print(f"Error saving paths: {e}")

    def get_path_names(self):
        """Get list of all path names."""
        return list(self.paths.keys())

    def add_path(self, name, points=None):
        """Add a new path or update existing one."""
        self.paths[name] = points if points is not None else []
        self.save()

    def delete_path(self, name):
        """Delete a path by name."""
        if name in self.paths:
            del self.paths[name]
            self.save()

    def get_path(self, name):
        """Get points for a specific path."""
        return self.paths.get(name, [])

    def update_path_points(self, name, points):
        """Update points for an existing path."""
        if name in self.paths:
            self.paths[name] = points
            self.save()
