# Placeholder for Artist model
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() # Assuming db is initialized in main.py and passed around or imported

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Add other relevant artist fields here (genre, profile_summary, etc.)
    status = db.Column(db.String(20), nullable=False, default=\'paused\') # e.g., \'active\', \'paused\'

    def __repr__(self):
        return f"<Artist {self.id}: {self.name} ({self.status})>"

