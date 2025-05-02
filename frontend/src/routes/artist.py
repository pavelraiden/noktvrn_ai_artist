import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, request, jsonify
from src.models.artist import db, Artist

artist_bp = Blueprint("artist_bp", __name__)

@artist_bp.route("/artists", methods=["GET"])
def get_artists():
    """Returns a list of all artists and their status."""
    try:
        artists = Artist.query.all()
        artist_list = [
            {"id": artist.id, "name": artist.name, "status": artist.status}
            for artist in artists
        ]
        return jsonify(artist_list), 200
    except Exception as e:
        # Log the error e
        return jsonify({"error": "Failed to retrieve artists"}), 500

@artist_bp.route("/artists/<int:artist_id>/status", methods=["PUT"])
def update_artist_status(artist_id):
    """Updates the status of a specific artist (e.g., 'active' or 'paused')."""
    data = request.get_json()
    new_status = data.get("status")

    if not new_status or new_status not in ["active", "paused"]:
        return jsonify({"error": "Invalid status provided. Must be 'active' or 'paused'."}), 400

    try:
        artist = Artist.query.get(artist_id)
        if not artist:
            return jsonify({"error": "Artist not found"}), 404

        artist.status = new_status
        db.session.commit()

        # Placeholder: Here you would trigger the actual backend logic
        # to start or pause the artist's pipeline (e.g., call another API,
        # update a flag in a shared queue/database the backend monitors).
        print(f"Triggering backend action for Artist {artist_id}: Set status to {new_status}")

        return jsonify({"id": artist.id, "name": artist.name, "status": artist.status}), 200

    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"error": "Failed to update artist status"}), 500

