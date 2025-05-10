#!/bin/bash

# Script to install and configure PostgreSQL on Ubuntu 24.04

# Exit immediately if a command exits with a non-zero status.
set -e

# Update package list
sudo apt-get update

# Install PostgreSQL and contrib package
sudo apt-get install -y postgresql postgresql-contrib

# Start and enable PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# --- Basic Configuration ---

# Note: Replace 'ai_artist_user' and 'your_strong_password' with secure credentials
DB_NAME="ai_artist_db"
DB_USER="ai_artist_user"
DB_PASSWORD="your_strong_password" # Use a strong password, ideally managed via secrets

# Switch to postgres user to run psql commands
sudo -u postgres psql <<EOF
-- Create the database
CREATE DATABASE $DB_NAME;

-- Create the database user
CREATE USER $DB_USER WITH PASSWORD 	$DB_PASSWORD	;

-- Grant privileges to the user on the database
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Optional: Grant specific privileges if needed (Example)
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $DB_USER;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO $DB_USER;

-- Exit psql
\q
EOF

# --- Network Configuration (Optional - Allow remote connections) ---
# By default, PostgreSQL only listens on localhost. Modify these files
# if the backend application runs on a different server than the database.
# Ensure firewall rules allow traffic on port 5432 from the backend server IP.

# Find postgresql.conf and pg_hba.conf paths (version might vary)
PG_CONF=$(sudo -u postgres psql -t -P format=unaligned -c 	show config_file	)
PG_HBA=$(sudo -u postgres psql -t -P format=unaligned -c 	show hba_file	)

# Example: Allow connections from any IP (less secure, refine in production)
# echo "listen_addresses = 	*	" | sudo tee -a "$PG_CONF"
# echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a "$PG_HBA"

# Example: Allow connections only from a specific IP range (replace with your VPC range)
# echo "host    all             all             10.0.0.0/16             md5" | sudo tee -a "$PG_HBA"

# Restart PostgreSQL to apply changes if config files were modified
# sudo systemctl restart postgresql

echo "PostgreSQL installation and basic configuration complete."
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Remember to use the password set in this script (	$DB_PASSWORD	) in your .env file."

