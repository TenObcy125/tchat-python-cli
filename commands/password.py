import bcrypt
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data.json"

class PasswordMiddleware:
    def __init__(self):
        self.hashed_password = None
        self.load_password()

    def set_password(self, password):
        """Set a new password and save it to file"""
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        self._save_password()

    def verify_password(self, password):
        """Verify if the provided password matches the stored one"""
        if not self.hashed_password:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password)

    def is_password_set(self):
        """Check if a password is set"""
        return self.hashed_password is not None and self.hashed_password != b''

    def _save_password(self):
        """Save hashed password to file"""
        data = {}
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                data = {}

        data["password"] = self.hashed_password.decode('utf-8') if self.hashed_password else ""
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def load_password(self):
        """Load hashed password from file"""
        if not DATA_FILE.exists():
            self.hashed_password = None
            return
            
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                stored_password = data.get("password", "")
                self.hashed_password = stored_password.encode('utf-8') if stored_password else None
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            self.hashed_password = None