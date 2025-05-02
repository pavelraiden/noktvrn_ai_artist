#!/bin/bash

# Script to set up logging directory and log rotation for AI Artist Platform

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting Logging Setup (Directory & Logrotate) ---"

# --- Define Log Directory and User ---
LOG_DIR="/var/log/ai_artist"
APP_USER="ai_artist_user" # <<< ADJUST THIS to the user running the app services
APP_GROUP="ai_artist_user" # <<< ADJUST THIS to the group for the user

# --- Create Log Directory ---
echo "Creating log directory: $LOG_DIR"
if [ ! -d "$LOG_DIR" ]; then
    sudo mkdir -p "$LOG_DIR"
    echo "Directory created."
else
    echo "Directory already exists."
fi

# --- Set Permissions ---
echo "Setting permissions for $LOG_DIR (Owner: $APP_USER:$APP_GROUP)"
# Ensure the user running the application can write to this directory
sudo chown -R "$APP_USER":"$APP_GROUP" "$LOG_DIR"
sudo chmod -R 755 "$LOG_DIR" # User: rwx, Group: rx, Others: rx (adjust if stricter needed)

# --- Configure Logrotate ---
LOGROTATE_CONF="/etc/logrotate.d/ai-artist"
echo "Configuring logrotate in $LOGROTATE_CONF..."

sudo tee "$LOGROTATE_CONF" > /dev/null <<EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 $APP_USER $APP_GROUP # Create new log files with correct permissions
    sharedscripts
    postrotate
        # Reload or signal the application if necessary after rotation
        # Example: systemctl reload your-app.service
    endscript
}
EOF

echo "Logrotate configuration created."

# --- Test Logrotate Configuration (Optional) ---
# echo "Testing logrotate configuration (dry run)..."
# sudo logrotate -d "$LOGROTATE_CONF"
# echo "Forcing log rotation (for testing)..."
# sudo logrotate -f "$LOGROTATE_CONF"

# --- Important Notes ---
echo ""
echo "--- Logging Setup Complete --- "
echo "Log directory $LOG_DIR created with permissions for $APP_USER."
echo "Logrotate configured to rotate logs daily and keep 7 days."
echo ""
echo "IMPORTANT:"
echo "1. Ensure the application (backend, frontend) is configured to write logs to $LOG_DIR."
echo "2. Implement error handling, failure logging (failed chains, broken loops), and Telegram notifications within the application code itself."
echo "3. Verify the user '$APP_USER' exists and matches the user running the systemd services."

