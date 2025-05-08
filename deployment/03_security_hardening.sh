#!/bin/bash

# Script to perform security hardening on Ubuntu 24.04 for AI Artist Platform

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting Security Hardening (UFW, Fail2ban, SSH) ---"

# --- Install UFW (Uncomplicated Firewall) ---
echo "Installing UFW..."
sudo apt-get update
sudo apt-get install -y ufw

# --- Configure UFW Rules ---
echo "Configuring UFW firewall rules..."
# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow essential ports
sudo ufw allow ssh       # Default port 22 (adjust if you change SSH port)
sudo ufw allow http      # Port 80
sudo ufw allow https     # Port 443

# Optional: Allow PostgreSQL port 5432 if accessed remotely (adjust source IP if possible)
# sudo ufw allow from <APP_SERVER_IP> to any port 5432 proto tcp

# Enable UFW
echo "Enabling UFW..."
sudo ufw enable # This might disconnect SSH if rule is not correctly set, run with caution!

echo "UFW Status:"
sudo ufw status verbose

# --- Install Fail2ban ---
echo "Installing Fail2ban..."
sudo apt-get install -y fail2ban

# --- Configure Fail2ban --- 
echo "Configuring Fail2ban..."
# Copy default jail configuration to a local file for overrides
JAIL_LOCAL="/etc/fail2ban/jail.local"
if [ ! -f "$JAIL_LOCAL" ]; then
    sudo cp /etc/fail2ban/jail.conf "$JAIL_LOCAL"
    echo "Created $JAIL_LOCAL"
fi

# Enable SSHD jail in jail.local (it's often enabled by default, but ensure it is)
# This example ensures the [sshd] section exists and is enabled
if ! sudo grep -q "^\[sshd\]" "$JAIL_LOCAL"; then
    echo "Adding [sshd] section to $JAIL_LOCAL..."
    sudo tee -a "$JAIL_LOCAL" > /dev/null <<EOF

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s
maxretry = 5
bantime = 1h
EOF
elif ! sudo grep -q "^enabled\s*=\s*true" "$JAIL_LOCAL" under "^\[sshd\]"; then
    echo "Ensuring [sshd] is enabled in $JAIL_LOCAL..."
    # This sed command is complex; manual check might be safer.
    # It tries to find [sshd] and set enabled=true if found, otherwise adds the block.
    # Basic approach: ensure enabled = true is uncommented under [sshd]
    sudo sed -i 	/^\s*\[sshd\]/,/^\[/ s/^\s*#*\s*enabled\s*=.*/enabled = true/	 "$JAIL_LOCAL"
fi

# Restart Fail2ban to apply changes
echo "Restarting Fail2ban service..."
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

echo "Fail2ban Status:"
sudo fail2ban-client status sshd

# --- Harden SSH Configuration ---
echo "Hardening SSH configuration (/etc/ssh/sshd_config)..."
SSH_CONFIG="/etc/ssh/sshd_config"

# Disable Root Login
echo "Disabling root login via SSH..."
sudo sed -i 	/^#*PermitRootLogin/c\PermitRootLogin no	 "$SSH_CONFIG"

# IMPORTANT: Disable Password Authentication ONLY IF SSH key-based login is confirmed working!
# Uncomment the following lines AFTER verifying you can log in with your SSH key.
# echo "Disabling password authentication (ensure SSH key works first!)..."
# sudo sed -i 	/^#*PasswordAuthentication/c\PasswordAuthentication no	 "$SSH_CONFIG"

# Optional: Change default SSH port (e.g., to 2222)
# Remember to update UFW rule: `sudo ufw allow 2222/tcp` and `sudo ufw delete allow ssh`
# echo "Changing SSH port (optional)..."
# sudo sed -i 	/^#*Port/c\Port 2222	 "$SSH_CONFIG"

# Restart SSH service to apply changes
echo "Restarting SSH service..."
sudo systemctl restart sshd

echo "--- Security Hardening Complete ---"
echo "Review UFW status, Fail2ban status, and ensure you can still SSH into the server."
echo "IMPORTANT: If you disabled password authentication, verify SSH key login NOW."

