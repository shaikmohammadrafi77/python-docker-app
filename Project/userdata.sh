#!/bin/bash

# Update the system
dnf update -y

# Install Python, pip, and git
dnf install -y python3.9 python3.9-pip git

# Upgrade pip
python3.9 -m pip install --upgrade pip

# Switch to ec2-user directory
cd /home/ec2-user

# Clone your GitHub repo (public repo)
git clone https://github.com/shaikmohammadrafi77/e-bugtracker.git

# Navigate into project folder
cd e-bugtracker/Project

# Create virtual environment
python3.9 -m venv venv

# Activate venv
source venv/bin/activate

# Install project dependencies
pip install -r requirements.txt

# Export Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Run your Flask app
nohup flask run --host=0.0.0.0 --port=5000 &
