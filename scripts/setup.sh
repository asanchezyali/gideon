#!/bin/bash
# Gideon Setup Script
# ====================
# Automated setup for Gideon development environment

set -e  # Exit on error

echo "================================"
echo "Gideon Setup"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo -e "${GREEN}✓ Python $python_version${NC}"
else
    echo -e "${RED}✗ Python 3.11+ required (found $python_version)${NC}"
    exit 1
fi

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -e ".[dev]" --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Setup .env file
echo -e "\n${YELLOW}Setting up configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Please edit .env with your API keys${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p .gideon/vectorstore
echo -e "${GREEN}✓ Directories created${NC}"

# Run tests
echo -e "\n${YELLOW}Running tests...${NC}"
if pytest tests/ --quiet; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${YELLOW}⚠ Some tests failed (this is OK for first setup)${NC}"
fi

echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"

echo -e "\nNext steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Activate environment: source venv/bin/activate"
echo "  3. Run gideon: gideon --help"
echo "  4. Try examples: cd examples/quickstart && python 01_basic_usage.py"

echo -e "\nFor Ollama (local LLM):"
echo "  curl https://ollama.ai/install.sh | sh"
echo "  ollama pull llama2"

echo ""
