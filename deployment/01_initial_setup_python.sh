#!/bin/bash

# Script to perform initial server setup and install Python 3.11 on Ubuntu 24.04

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting Initial Server Setup & Python 3.11 Installation ---"

# --- Update System Packages ---
echo "Updating package lists..."
sudo apt-get update
echo "Upgrading existing packages (optional but recommended)..."
sudo apt-get upgrade -y

# --- Install Prerequisites ---
echo "Installing prerequisite packages..."
sudo apt-get install -y software-properties-common wget git curl

# --- Add Deadsnakes PPA for Python versions ---
echo "Adding deadsnakes PPA..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update # Update package list again after adding PPA

# --- Install Python 3.11 ---
echo "Installing Python 3.11 and related packages..."
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# --- Verify Python Installation ---
echo "Verifying Python 3.11 installation..."
python3.11 --version

# --- Install pip for Python 3.11 (if not installed as python3-pip) ---
# Check if pip is available for python3.11
if ! python3.11 -m pip --version &> /dev/null; then
    echo "Installing pip for Python 3.11..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
fi
echo "Verifying pip for Python 3.11..."
python3.11 -m pip --version

# --- Install Git (if not already installed) ---
echo "Ensuring Git is installed..."
sudo apt-get install -y git
git --version

# --- Set Python 3.11 as default python3 (Optional) ---
# Uncomment the following lines if you want python3.11 to be the default `python3`
# echo "Setting Python 3.11 as default python3 (optional)..."
# sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
# Verify default python3 version
# python3 --version

echo "--- Initial Server Setup & Python 3.11 Installation Complete ---"

