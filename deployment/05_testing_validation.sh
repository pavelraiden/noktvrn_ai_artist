#!/bin/bash

# Script to guide testing and validation of the deployed AI Artist Platform

# Exit immediately if a command exits with a non-zero status.
# set -e # Commented out as this is mostly instructional

echo "--- Starting AI Artist Platform Testing & Validation Guide ---"

# --- Prerequisites ---
echo "Ensure the following before starting tests:"
echo "1. All services (PostgreSQL, Nginx, Gunicorn, Backend Runner) are running."
echo "   - Check with: sudo systemctl status ai_artist_frontend.service ai_artist_backend.service nginx.service postgresql.service"
echo "2. The .env file is correctly populated with production keys and paths."
echo "3. You can access the frontend dashboard via its HTTPS URL."

# --- Environment Setup (Run these in the server's shell) ---
APP_DIR="/path/to/your/ai_artist_system_clone" # <<< ADJUST THIS PATH
VENV_DIR="$APP_DIR/venv"

# Activate virtual environment (adjust path if needed)
# source "$VENV_DIR/bin/activate"

echo ""
echo "--- Test 1: Basic Service Accessibility ---"
echo "1. Access the frontend dashboard URL in your browser. It should load without errors."
echo "2. Check Nginx logs for errors: sudo tail -n 50 /var/log/nginx/ai-artist-ssl-error.log"
echo "3. Check Gunicorn logs for errors: sudo tail -n 50 /var/log/gunicorn/ai-artist-error.log /var/log/gunicorn/ai-artist-frontend-stderr.log"

echo ""
echo "--- Test 2: Database Connection ---"
echo "1. Check if the backend service started without DB connection errors:"
echo "   sudo tail -n 50 /var/log/ai_artist/backend-stderr.log"
echo "2. (Optional) Connect to PostgreSQL and verify tables exist:"
echo "   sudo -u postgres psql ai_artist_db -c 	\dt	"

# --- Test 3: API Key Validation (Indirect) ---
echo "1. Monitor backend logs while triggering actions that use APIs (e.g., starting an artist cycle)."
echo "   sudo tail -f /var/log/ai_artist/backend-stdout.log /var/log/ai_artist/backend-stderr.log"
echo "2. Look for any authentication errors or API-related failures."

echo ""
echo "--- Test 4: Telegram Preview ---"
echo "1. Ensure the TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are correct in the .env file."
echo "2. Trigger an action that should send a Telegram message (e.g., a specific stage in the artist cycle)."
echo "3. Verify the message is received in the target Telegram chat ($TELEGRAM_CHAT_ID)."
echo "4. Check backend logs for any Telegram API errors."

echo ""
echo "--- Test 5: Core LLM Chain ---"
echo "1. Trigger a part of the workflow that involves an LLM call (e.g., prompt generation)."
echo "2. Monitor backend logs for successful LLM API interaction and expected output."
echo "   sudo tail -f /var/log/ai_artist/backend-stdout.log /var/log/ai_artist/backend-stderr.log"

echo ""
echo "--- Test 6: Admin Dashboard - Start/Pause Functionality ---"
echo "1. Open the admin dashboard in your browser."
echo "2. Select an artist."
echo "3. Click the 	Pause	 button. Verify the status updates on the dashboard and check backend logs."
echo "4. Click the 	Start	 button. Verify the status updates and check backend logs for confirmation that the artist process resumes."
echo "5. Check the database to confirm the artist	"s status field is updated correctly."

echo ""
echo "--- Test 7: Full Artist Test Cycle ---"
echo "1. Use the admin dashboard or backend mechanism to start a cycle for one test artist."
echo "2. Monitor the entire process through backend logs:"
echo "   sudo tail -f /var/log/ai_artist/backend-stdout.log /var/log/ai_artist/backend-stderr.log"
echo "3. Verify:
    - Media generation (images, audio) occurs and files are saved to the expected output directory.
    - Database records are updated correctly (e.g., cycle count, status, output paths).
    - Telegram previews are sent at appropriate stages.
    - The cycle completes successfully without crashing."

echo ""
echo "--- Test 8: Logging and Error Handling ---"
echo "1. Intentionally trigger an error (if possible without disrupting production) or review logs for past errors."
echo "2. Verify that errors are logged clearly in /var/log/ai_artist/backend-stderr.log or specific error logs."
echo "3. Check if log rotation is working: ls -l /var/log/ai_artist/ (look for rotated/compressed files after a day)."

echo ""
echo "--- Test 9: Security Checks ---"
echo "1. Verify UFW is active: sudo ufw status"
echo "2. Verify Fail2ban is active and banning IPs (if attacks occurred): sudo fail2ban-client status sshd"
echo "3. Confirm SSH root login is disabled and password authentication is disabled (if intended)."

echo ""
echo "--- Testing & Validation Guide Complete ---"
echo "Document all test results, especially any failures or unexpected behavior."

