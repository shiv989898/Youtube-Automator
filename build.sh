#!/bin/bash
# Install system dependencies
apt-get update
apt-get install -y ffmpeg fonts-dejavu-core

# Install Python dependencies
pip install -r requirements.txt
