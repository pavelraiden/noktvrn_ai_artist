import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
# Import db instance from the models module where it's defined
from src.models.artist import db, Artist
# Import user blueprint (if still needed)
from src.routes.user import user_bp
# Import the new artist blueprint
from src.routes.artist import artist_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key-change-me') # Use env var for secret key

# Configure PostgreSQL connection using environment variables
# These should match the service name and credentials in docker-compose.yml
DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_HOST = os.getenv('DB_HOST', 'db') # Service name in docker-compose
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'ai_artist_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
# app.register_blueprint(artist_bp, url_prefix='/api') # Will uncomment when artist_bp is created

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    # Add a dummy artist for testing if none exist
    if not Artist.query.first():
        dummy_artist = Artist(name='Dummy Artist 1', status='paused')
        db.session.add(dummy_artist)
        db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            # If index.html doesn't exist, maybe return a simple API status for root?
            # Or just the 404 for a file not found.
            # For now, let's keep the 404 for missing index.html
            return "index.html not found", 404

# Simple health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    # Use 0.0.0.0 to be accessible externally (within Docker network)
    # Debug should be False in production, controlled by FLASK_ENV perhaps
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_ENV') == 'development')

