#!/bin/bash
# PassCraft Kali Linux Installer
# Version: 2.0
#Author:Sabir Khan

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create virtual environment
echo -e "${YELLOW}[1/4] Creating virtual environment...${NC}"
python3 -m venv passcraft-venv || {
    echo -e "${RED}ERROR: Failed to create virtual environment${NC}"
    echo "Install python3-venv first: sudo apt install python3-venv"
    exit 1
}

# Activate venv
source passcraft-venv/bin/activate

# Install dependencies
echo -e "${YELLOW}[2/4] Installing system dependencies...${NC}"
sudo apt install -y \
    python3-dev \
    build-essential \
    libgl1-mesa-dev \
    libxcb-xinerama0 || {
    echo -e "${RED}ERROR: Failed to install system packages${NC}"
    exit 1
}

# Install PyQt6 in venv
echo -e "${YELLOW}[3/4] Installing PyQt6...${NC}"
pip install --upgrade pip wheel setuptools
pip install PyQt6 || {
    echo -e "${RED}ERROR: PyQt6 installation failed${NC}"
    exit 1
}

# Verify
echo -e "${YELLOW}[4/4] Verifying installation...${NC}"
python3 -c "from PyQt6.QtWidgets import QApplication; QApplication([])" && \
    echo -e "${GREEN}✓ Installation successful!${NC}" || {
    echo -e "${RED}ERROR: Verification failed${NC}"
    exit 1
}

echo -e "\n${GREEN}Run PassCraft5 with:${NC}"
echo "source passcraft-venv/bin/activate"
echo "python3 passcraft5.py"
