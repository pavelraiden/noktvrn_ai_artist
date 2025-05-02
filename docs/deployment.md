# AI Artist Platform - Production Deployment Guide (Vultr - v1.2)

This guide details the steps to manually deploy the AI Artist Platform (v1.2 - Batch Runner focus) onto a Vultr server running Ubuntu 24.04 LTS.

**Target Server:**
*   **IP Address:** 136.244.94.146 (Example - Use your actual server IP)
*   **OS:** Ubuntu 24.04 LTS (or closest LTS)
*   **Specs:** 4 vCPU, 16GB RAM, SSD storage (e.g., Vultr Plan: `voc-g-4c-16gb-80s-amd`)
*   **Region:** Frankfurt (fra) or preferred European region

**Prerequisites:**
*   SSH access to the server as the `root` user or a user with `sudo` privileges.
*   A GitHub Personal Access Token (PAT) with repo access if the repository is private.
*   API keys and credentials as listed in `.env.example`.

## Deployment Steps

Execute these steps sequentially on the Vultr server via SSH.

**1. Initial Server Setup & Python Installation**

*   Connect to the server via SSH.
*   Run the following commands:
    ```bash
    sudo apt-get update && sudo apt-get upgrade -y
    sudo apt-get install -y python3.11 python3.11-venv python3-pip git ffmpeg
    # Verify installations
    python3.11 --version
    pip3 --version
    git --version
    ffmpeg -version
    ```

**2. Security Hardening**

*   **IMPORTANT:** Set up SSH key-based authentication and disable password authentication for enhanced security.
*   Install and configure UFW (firewall):
    ```bash
    sudo apt-get install -y ufw
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh # Or your custom SSH port
    # Add other rules if needed (e.g., for monitoring)
    sudo ufw enable
    sudo ufw status verbose
    ```
*   Install Fail2ban (brute-force protection):
    ```bash
    sudo apt-get install -y fail2ban
    sudo systemctl enable fail2ban
    sudo systemctl start fail2ban
    sudo fail2ban-client status sshd
    ```
*   Disable root login via SSH (edit `/etc/ssh/sshd_config` and set `PermitRootLogin no`, then `sudo systemctl restart sshd`). Ensure you have another user with `sudo` access first!

**3. Create Application User**

*   Create a dedicated user to run the application:
    ```bash
    sudo adduser ai_artist_app
    # Grant sudo privileges if necessary (use with caution)
    # sudo usermod -aG sudo ai_artist_app
    ```

**4. Clone Application Repository**

*   Log in as the `ai_artist_app` user: `su - ai_artist_app`
*   Clone the repository (use PAT for private repos):
    ```bash
    cd ~
    # Replace <YOUR_PAT> with your GitHub Personal Access Token
    # git clone https://<YOUR_PAT>@github.com/pavelraiden/noktvrn_ai_artist.git
    # Or for public repo:
    git clone https://github.com/pavelraiden/noktvrn_ai_artist.git
    cd noktvrn_ai_artist
    APP_DIR=$(pwd) # Store the application directory path
    echo "Application cloned to: $APP_DIR"
    ```

**5. Set Up Python Virtual Environment & Dependencies**

*   Navigate to the application directory (`cd $APP_DIR`).
*   Create and activate the virtual environment:
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```
*   Install dependencies (including `moviepy` for video editing):
    ```bash
    pip install -r requirements.txt
    ```

**6. Configure Production Environment (.env)**

*   Copy the template:
    ```bash
    cp .env.example .env
    ```
*   **Edit the `.env` file** using a text editor (like `nano .env`):
    *   Fill in **all** required API keys (Suno, Pexels, LLMs, Telegram Bot Token).
    *   Set the correct `TELEGRAM_CHAT_ID`.
    *   Adjust `OUTPUT_BASE_DIR` if needed (default is `$APP_DIR/output`).
    *   Configure `LOG_LEVEL` (e.g., `INFO`, `DEBUG`).
    *   Configure A/B testing: Set `AB_TESTING_ENABLED=True` or `False`.
    *   Verify all other settings.
*   Secure the `.env` file:
    ```bash
    chmod 600 .env
    ```

**7. Prepare Data and Log Directories**

*   Ensure the necessary directories exist and have correct permissions. The `artist_db_service.py` and `batch_runner.py` attempt to create these, but manual setup ensures correct ownership.
    ```bash
    mkdir -p $APP_DIR/data
    mkdir -p $APP_DIR/logs
    mkdir -p $APP_DIR/output/run_status
    mkdir -p $APP_DIR/output/approved
    # Ensure the app user owns these directories
    # (Should be owned by ai_artist_app if created after su - ai_artist_app)
    # sudo chown -R ai_artist_app:ai_artist_app $APP_DIR/data $APP_DIR/logs $APP_DIR/output
    ```
*   The SQLite database (`$APP_DIR/data/artists.db`) will be created automatically when the batch runner starts if it doesn't exist.

**8. Configure Systemd Service for Batch Runner**

*   Create a systemd service file to manage the batch runner process.
*   As root or using `sudo`, create the file `/etc/systemd/system/ai_artist_batch_runner.service`:
    ```ini
    [Unit]
    Description=AI Artist Batch Runner Service
    After=network.target

    [Service]
    User=ai_artist_app
    Group=ai_artist_app
    WorkingDirectory=/home/ai_artist_app/noktvrn_ai_artist # Adjust if cloned elsewhere
    EnvironmentFile=/home/ai_artist_app/noktvrn_ai_artist/.env # Adjust path
    ExecStart=/home/ai_artist_app/noktvrn_ai_artist/venv/bin/python /home/ai_artist_app/noktvrn_ai_artist/batch_runner/artist_batch_runner.py # Adjust paths
    Restart=always
    RestartSec=10
    StandardOutput=append:/home/ai_artist_app/noktvrn_ai_artist/logs/batch_runner_stdout.log # Adjust path
    StandardError=append:/home/ai_artist_app/noktvrn_ai_artist/logs/batch_runner_stderr.log # Adjust path

    [Install]
    WantedBy=multi-user.target
    ```
*   **Important:** Adjust all paths in the service file (`WorkingDirectory`, `EnvironmentFile`, `ExecStart`, `StandardOutput`, `StandardError`) to match your actual application directory and user home.
*   Reload Systemd, enable, and start the service:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable ai_artist_batch_runner.service
    sudo systemctl start ai_artist_batch_runner.service
    ```

**9. Verify Service Status and Logs**

*   Check the service status:
    ```bash
    sudo systemctl status ai_artist_batch_runner.service
    ```
*   Monitor the logs:
    ```bash
    tail -f /home/ai_artist_app/noktvrn_ai_artist/logs/batch_runner.log
    tail -f /home/ai_artist_app/noktvrn_ai_artist/logs/batch_runner_stdout.log
    tail -f /home/ai_artist_app/noktvrn_ai_artist/logs/batch_runner_stderr.log
    ```
*   Check for the creation of the SQLite database: `ls -l $APP_DIR/data/artists.db`
*   Check the `output/run_status` directory for run files.
*   Check Telegram for messages from the bot.

## Updating the Deployment

1.  Log in as `ai_artist_app`.
2.  Navigate to the application directory: `cd $APP_DIR`
3.  Stop the service: `sudo systemctl stop ai_artist_batch_runner.service`
4.  Pull the latest code: `git pull origin main` (or your branch)
5.  Activate the virtual environment: `source venv/bin/activate`
6.  Update dependencies: `pip install -r requirements.txt`
7.  Apply any necessary configuration changes (e.g., to `.env`).
8.  Restart the service: `sudo systemctl start ai_artist_batch_runner.service`
9.  Monitor logs.

## Post-Deployment

*   Monitor logs regularly for errors.
*   Keep the system updated (`sudo apt-get update && sudo apt-get upgrade -y`).
*   Consider setting up more robust monitoring and alerting.

This completes the manual deployment process for the AI Artist Batch Runner (v1.2) on the Vultr server.

