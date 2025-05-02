# Gunicorn configuration file for AI Artist Platform Frontend (Flask)

import multiprocessing

# --- Server Socket ---
# Bind to a Unix socket (recommended for use with Nginx)
# Ensure the directory exists and has correct permissions for Gunicorn user
# Replace /path/to/your/ with the actual deployment path
bind = "unix:/path/to/your/gunicorn.sock" # <<< ADJUST THIS PATH
# Alternatively, bind to a local port (less common with Nginx)
# bind = "127.0.0.1:5000"

# --- Worker Processes ---
# Number of worker processes. A common recommendation is (2 * cpu_cores) + 1.
# Adjust based on server resources and expected load.
workers = multiprocessing.cpu_count() * 2 + 1

# Type of workers (sync is default, consider gevent for I/O bound apps if needed)
# worker_class = "sync"

# --- Security ---
# User and group to run as. Create a dedicated user or use www-data if appropriate.
# Ensure this user has permissions to access the socket file and application code.
# user = "ai_artist_user" # <<< ADJUST OR CREATE THIS USER
# group = "www-data" # <<< ADJUST OR CREATE THIS GROUP

# --- Logging ---
# Access log file path
accesslog = "/var/log/gunicorn/ai-artist-access.log"
# Error log file path
errorlog = "/var/log/gunicorn/ai-artist-error.log"
# Log level (debug, info, warning, error, critical)
loglevel = "info"

# --- Process Naming ---
# Helps identify the Gunicorn processes
proc_name = "ai_artist_frontend"

# --- Application ---
# Change directory to the application source directory before loading
# Adjust the path based on your deployment structure
chdir = "/path/to/your/ai_artist_system_clone/frontend" # <<< ADJUST THIS PATH
# WSGI application path (module:variable)
# Assumes your Flask app instance is named `app` in `src/main.py`
wsgi_app = "src.main:app"

# --- Other Settings ---
# Daemonize the process (False if managed by Systemd/Supervisor)
daemon = False

# Timeout for worker processes (seconds)
timeout = 120

# Number of requests a worker will process before restarting
# Helps prevent memory leaks
# max_requests = 1000
# max_requests_jitter = 50

