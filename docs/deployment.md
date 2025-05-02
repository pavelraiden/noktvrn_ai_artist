# AI Artist Platform - Production Deployment Guide (Vultr)

This guide details the steps to manually deploy the AI Artist Platform onto a Vultr server running Ubuntu 24.04 LTS.

**Target Server:**
*   **IP Address:** 136.244.94.146
*   **OS:** Ubuntu 24.04 LTS (Note: Original plan specified 22.04, but 24.04 was used due to Vultr availability)
*   **Specs:** 4 vCPU, 16GB RAM, 80GB SSD (Vultr Plan: `voc-g-4c-16gb-80s-amd`)
*   **Region:** Frankfurt (fra)

**Prerequisites:**
*   SSH access to the server (136.244.94.146) as the `root` user (initial password: `mR#6r]JZqcU2({.v`). **It is critical to change this password or set up SSH key authentication immediately.**
*   The deployment scripts and configuration files generated in the `/deployment/` directory of the `noktvrn_ai_artist` repository.
*   A domain name pointed to the server IP (optional, for Let's Encrypt SSL).

## Deployment Steps

Execute these steps sequentially on the Vultr server via SSH.

**1. Initial Server Setup & Python Installation**

*   Copy the `deployment/01_initial_setup_python.sh` script to the server.
*   Make it executable: `chmod +x 01_initial_setup_python.sh`
*   Run the script: `sudo ./01_initial_setup_python.sh`
*   This script updates the system, installs Python 3.11, pip, venv, and Git.

**2. Security Hardening**

*   **IMPORTANT:** Before running the hardening script, ensure you have set up SSH key-based authentication if you intend to disable password authentication. Test key-based login in a separate terminal session first.
*   Copy the `deployment/03_security_hardening.sh` script to the server.
*   Make it executable: `chmod +x 03_security_hardening.sh`
*   Review the script, especially the SSH hardening section (PasswordAuthentication).
*   Run the script: `sudo ./03_security_hardening.sh`
*   This script installs and configures UFW (firewall), Fail2ban (brute-force protection), and hardens SSH settings (disables root login).
*   Verify UFW status (`sudo ufw status verbose`) and Fail2ban status (`sudo fail2ban-client status sshd`).

**3. Create Application User**

*   Create a dedicated user to run the application services (replace `ai_artist_user` if desired).
    ```bash
    sudo adduser ai_artist_user
    # Add user to sudo group if needed for specific tasks, otherwise avoid
    # sudo usermod -aG sudo ai_artist_user
    # Add user to www-data group to allow Gunicorn/Nginx interaction if needed
    sudo usermod -aG www-data ai_artist_user
    ```

**4. PostgreSQL Installation & Configuration**

*   Copy the `deployment/02_install_configure_postgres.sh` script to the server.
*   **Edit the script:** Replace `YourStrongPasswordHere` with a strong, unique password for the `ai_artist_user` database user. Record this password securely.
*   Make the script executable: `chmod +x 02_install_configure_postgres.sh`
*   Run the script: `sudo ./02_install_configure_postgres.sh`
*   This script installs PostgreSQL, creates the `ai_artist_db` database and `ai_artist_user`, grants privileges, and sets up a daily backup cron job.

**5. Clone Application Repository**

*   Log in as the `ai_artist_user` (or switch user: `su - ai_artist_user`).
*   Clone the repository into the user's home directory (or another chosen location, e.g., `/srv/ai_artist`). Remember to adjust paths in subsequent steps if you change the location.
    ```bash
    cd ~
    # Use the provided GitHub PAT for cloning private repo
    git clone https://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@github.com/pavelraiden/noktvrn_ai_artist.git
    cd noktvrn_ai_artist
    APP_DIR=$(pwd) # Store the application directory path
    echo "Application cloned to: $APP_DIR"
    ```

**6. Set Up Python Virtual Environment & Dependencies**

*   Navigate to the application directory (`cd $APP_DIR`).
*   Create a virtual environment using the installed Python 3.11:
    ```bash
    python3.11 -m venv venv
    ```
*   Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
*   Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

**7. Configure Production Environment (.env)**

*   Copy the template: `cp deployment/env.production.template .env`
*   **Edit the `.env` file:**
    *   Replace `YourStrongPasswordHere` in `DATABASE_URL` with the actual PostgreSQL password you set.
    *   Replace `generate_a_strong_random_secret_key_here` for `FLASK_SECRET_KEY` with a newly generated strong secret key (e.g., using `openssl rand -hex 32`).
    *   Adjust `OUTPUT_BASE_DIR`, `RELEASE_LOG_FILE`, `RELEASE_QUEUE_FILE` paths to match the deployment structure (e.g., `$APP_DIR/output`).
    *   Verify all API keys are correct.
*   Secure the `.env` file:
    ```bash
    chmod 600 .env
    ```

**8. Install & Configure Nginx and Gunicorn**

*   Install Nginx and Gunicorn (outside the venv, globally):
    ```bash
    sudo apt-get update
    sudo apt-get install -y nginx gunicorn
    ```
*   Copy the Nginx configuration:
    *   Edit `deployment/nginx_ai_artist.conf`: Replace `your_domain_or_ip` with the server's IP (136.244.94.146) or your domain name. Adjust `alias` and `proxy_pass` paths to match `$APP_DIR`.
    *   Copy to Nginx sites-available: `sudo cp deployment/nginx_ai_artist.conf /etc/nginx/sites-available/ai_artist`
    *   Enable the site: `sudo ln -s /etc/nginx/sites-available/ai_artist /etc/nginx/sites-enabled/`
    *   Remove the default site if it exists: `sudo rm /etc/nginx/sites-enabled/default`
    *   Test Nginx configuration: `sudo nginx -t`
*   Create SSL directory and generate self-signed certificate (or use Let's Encrypt later):
    ```bash
    sudo mkdir -p /etc/nginx/ssl
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/ai_artist_selfsigned.key -out /etc/nginx/ssl/ai_artist_selfsigned.crt
    # Answer the prompts for the certificate details
    sudo chmod 600 /etc/nginx/ssl/ai_artist_selfsigned.key
    ```
*   Restart Nginx: `sudo systemctl restart nginx`
*   Create Gunicorn log directory:
    ```bash
    sudo mkdir -p /var/log/gunicorn
    sudo chown ai_artist_user:www-data /var/log/gunicorn # Adjust user/group as needed
    sudo chmod 775 /var/log/gunicorn
    ```

**9. Configure Systemd Services**

*   Copy the Gunicorn configuration:
    *   Edit `deployment/gunicorn_config.py`: Adjust `bind` (socket path), `user`, `group`, and `chdir` paths to match `$APP_DIR` and the `ai_artist_user`.
*   Copy the Systemd service files:
    *   Edit `deployment/ai_artist_frontend.service`: Adjust `User`, `Group`, `WorkingDirectory`, `EnvironmentFile` (if used), and `ExecStart` paths to match `$APP_DIR`, the virtual environment (`$APP_DIR/venv`), and the Gunicorn config path.
    *   Edit `deployment/ai_artist_backend.service`: Adjust `User`, `Group`, `WorkingDirectory`, `EnvironmentFile`, and `ExecStart` paths to match `$APP_DIR` and the virtual environment.
    *   Copy to Systemd: `sudo cp deployment/ai_artist_frontend.service deployment/ai_artist_backend.service /etc/systemd/system/`
*   Reload Systemd, enable, and start the services:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable ai_artist_frontend.service
    sudo systemctl start ai_artist_frontend.service
    sudo systemctl enable ai_artist_backend.service
    sudo systemctl start ai_artist_backend.service
    ```
*   Check service status:
    ```bash
    sudo systemctl status ai_artist_frontend.service
    sudo systemctl status ai_artist_backend.service
    ```

**10. Set Up Logging Directory**

*   Copy `deployment/04_logging_setup.sh` to the server.
*   Edit the script: Ensure `APP_USER` and `APP_GROUP` match the user running the services (`ai_artist_user`).
*   Make it executable: `chmod +x 04_logging_setup.sh`
*   Run the script: `sudo ./04_logging_setup.sh`
*   This creates `/var/log/ai_artist` and configures logrotate.

**11. Testing and Validation**

*   Copy `deployment/05_testing_validation.sh` to the server.
*   Review the script and adjust any paths (`APP_DIR`).
*   Execute the tests outlined in the script, monitoring logs closely:
    *   `sudo tail -f /var/log/nginx/ai-artist-ssl-access.log`
    *   `sudo tail -f /var/log/nginx/ai-artist-ssl-error.log`
    *   `sudo tail -f /var/log/gunicorn/ai-artist-error.log`
    *   `sudo tail -f /var/log/ai_artist/backend-stdout.log`
    *   `sudo tail -f /var/log/ai_artist/backend-stderr.log`
*   Access the dashboard via `https://136.244.94.146` (accept the self-signed certificate warning).
*   Perform tests for API keys, Telegram, LLM chain, Start/Pause, and a full artist cycle.

**12. (Optional) Let's Encrypt SSL**

*   If you have a domain name pointed to the server IP:
    ```bash
    sudo apt-get install certbot python3-certbot-nginx
    sudo certbot --nginx -d your_domain_name.com # Replace with your domain
    # Follow prompts. Certbot will modify Nginx config automatically.
    sudo systemctl restart nginx
    ```

## Post-Deployment

*   Monitor logs regularly.
*   Ensure backups are running (`ls -l /var/backups/postgres`).
*   Keep the system updated (`sudo apt-get update && sudo apt-get upgrade -y`).

This completes the manual deployment process. The AI Artist Platform should now be running on the Vultr server.

