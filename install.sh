#!/bin/bash
# PassCraft5 PyQt6 Installation Script (Forced Mode)
# Author: Your Name
# Version: 1.2

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
python_check() {
    echo -e "${YELLOW}[1/4] Checking Python environment...${NC}"
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}ERROR: Python3 not found!${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ "$PYTHON_VERSION" < "3.8" ]]; then
        echo -e "${RED}Requires Python ≥3.8 (Found: $PYTHON_VERSION)${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
}

# System dependencies (Linux/macOS)
install_deps() {
    echo -e "${YELLOW}[2/4] Installing system dependencies...${NC}"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Debian/Ubuntu
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y \
                python3-dev \
                build-essential \
                libgl1-mesa-dev \
                libxcb-xinerama0 \
                libxkbcommon-x11-0 \
                qt6-base-dev
        # RHEL/CentOS
        elif command -v yum &> /dev/null; then
            sudo yum install -y \
                python3-devel \
                gcc-c++ \
                mesa-libGL-devel \
                qt6-qtbase-devel
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install qt@6 pkg-config
    fi
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Force install PyQt6 with fallbacks
install_pyqt6() {
    echo -e "${YELLOW}[3/4] Forcing PyQt6 installation...${NC}"
    
    # Attempt 1: Normal pip install
    if pip install --upgrade PyQt6 PyQt6-Qt6 PyQt6-sip; then
        echo -e "${GREEN}✓ PyQt6 installed via pip${NC}"
        return
    fi
    
    # Attempt 2: Build from source
    echo -e "${YELLOW}Retrying with source build...${NC}"
    pip install --upgrade pip wheel setuptools
    pip install PyQt6 --no-binary PyQt6
    
    # Verify installation
    if python3 -c "from PyQt6.QtWidgets import QApplication; QApplication([])"; then
        echo -e "${GREEN}✓ PyQt6 verification passed${NC}"
    else
        echo -e "${RED}CRITICAL: PyQt6 failed to initialize!${NC}"
        exit 1
    fi
}

# Post-install checks
verify_installation() {
    echo -e "${YELLOW}[4/4] Running diagnostics...${NC}"
    
    cat << EOF > qt_test.py
from PyQt6.QtWidgets import QApplication, QLabel
app = QApplication([])
label = QLabel("PassCraft5: PyQt6 Working!")
label.show()
app.exec()
EOF

    if python3 qt_test.py &> /dev/null; then
        echo -e "${GREEN}✓ GUI test successful!${NC}"
        rm qt_test.py
    else
        echo -e "${RED}GUI test failed! Check these:${NC}"
        echo "1. Run 'export QT_DEBUG_PLUGINS=1' before debugging"
        echo "2. Check libxcb dependencies on Linux"
        exit 1
    fi
}

# Main execution
python_check
install_deps
install_pyqt6
verify_installation

echo -e "\n${GREEN}PassCraft5 environment ready! Run:${NC}"
echo "python3 passcraft5.py"
