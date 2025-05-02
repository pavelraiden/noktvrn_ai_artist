#!/bin/bash

# Script to install and configure PostgreSQL on Ubuntu 24.04 for AI Artist Platform

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting PostgreSQL Installation & Configuration ---"

# --- Installation ---
echo "Updating package lists..."
sudo apt-get update
echo "Installing PostgreSQL and contrib package..."
sudo apt-get install -y postgresql postgresql-contrib

# --- Service Management ---
echo "Starting and enabling PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# --- Basic Configuration ---
echo "Configuring database and user..."

# IMPORTANT: Replace 'YourStrongPasswordHere' with a secure, generated password.
# Store this password securely and use it in the .env file.
DB_NAME="ai_artist_db"
DB_USER="ai_artist_user"
DB_PASSWORD="YourStrongPasswordHere" # <<< REPLACE THIS!

# Check if user/db already exist to make script idempotent (optional but good practice)
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname=	$DB_NAME	")
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname=	$DB_USER	")

if [ "$DB_EXISTS" = 	1	 ]; then
    echo "Database 	$DB_NAME	 already exists."
else
    echo "Creating database: $DB_NAME"
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
fi

if [ "$USER_EXISTS" = 	1	 ]; then
    echo "User 	$DB_USER	 already exists. Setting password..."
    # Use ALTER USER if user exists but ensure password is set
    sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD 	$DB_PASSWORD	;"
else
    echo "Creating user: $DB_USER"
    # Use single quotes around the password in the SQL command
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD 	$DB_PASSWORD	;"
fi

echo "Granting privileges to user $DB_USER on database $DB_NAME..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Optional: Grant specific privileges if needed (Example)
# sudo -u postgres psql -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $DB_USER;"
# sudo -u postgres psql -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO $DB_USER;"

# --- Network Configuration --- 
echo "Configuring network settings (defaulting to localhost)..."
# By default, PostgreSQL 14+ listens only on localhost (127.0.0.1), which is secure.
# If your application runs on the same server, no changes are needed here.
# If the app is on a different server, you must:
# 1. Edit postgresql.conf to change `listen_addresses` (e.g., `listen_addresses = 	*	` or specific IPs).
# 2. Edit pg_hba.conf to allow connections from the app server	"s IP address using md5 authentication.
# 3. Ensure your firewall (ufw) allows TCP traffic on port 5432 from the app server	"s IP.

# Example commands (Uncomment and modify if remote access is needed):
# PG_CONF=$(sudo -u postgres psql -t -P format=unaligned -c 	show config_file	)
# PG_HBA=$(sudo -u postgres psql -t -P format=unaligned -c 	show hba_file	)
# echo "listen_addresses = 	*	" | sudo tee -a "$PG_CONF"
# echo "host    $DB_NAME    $DB_USER    <APP_SERVER_IP>/32    md5" | sudo tee -a "$PG_HBA"
# sudo systemctl restart postgresql

# --- Auto-Backup Setup (using pg_dump and cron) ---
echo "Setting up daily database backup..."
BACKUP_DIR="/var/backups/postgres"
sudo mkdir -p "$BACKUP_DIR"
sudo chown postgres:postgres "$BACKUP_DIR"
sudo chmod 700 "$BACKUP_DIR"

# Create backup script
BACKUP_SCRIPT="/usr/local/bin/backup_postgres.sh"
sudo tee "$BACKUP_SCRIPT" > /dev/null <<EOF
#!/bin/bash
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/$DB_NAME-\$TIMESTAMP.sql.gz"
PGPASSWORD="$DB_PASSWORD" pg_dump -U "$DB_USER" -h localhost -d "$DB_NAME" | gzip > "\$BACKUP_FILE"
# Optional: Remove backups older than 7 days
find "$BACKUP_DIR" -type f -name 	*.sql.gz	 -mtime +7 -delete
EOF

sudo chmod +x "$BACKUP_SCRIPT"

# Add cron job to run daily at 3 AM
# Check if cron job already exists
if ! sudo crontab -l -u postgres | grep -q "$BACKUP_SCRIPT"; then
    echo "Adding cron job for daily backup..."
    (sudo crontab -l -u postgres 2>/dev/null; echo "0 3 * * * $BACKUP_SCRIPT") | sudo crontab -u postgres -
else
    echo "Cron job for backup already exists."
fi

echo "--- PostgreSQL Installation & Configuration Complete ---"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: Set to the value you replaced in this script."
echo "Daily backups configured to run at 3 AM, stored in $BACKUP_DIR"

