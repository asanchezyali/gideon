#!/bin/bash
# Quick Test Script
# =================
# Runs a quick test to verify Gideon is working

echo "================================"
echo "Gideon Quick Test"
echo "================================"

# Test CLI is installed
echo -e "\n1. Testing CLI installation..."
if command -v gideon &> /dev/null; then
    echo "✓ gideon command found"
    gideon --help | head -5
else
    echo "✗ gideon command not found"
    echo "  Run: pip install -e ."
    exit 1
fi

# Test imports
echo -e "\n2. Testing Python imports..."
python3 -c "
from src.gideon.llm.factory import LLMServiceFactory
from src.gideon.search import SemanticSearchEngine
from src.gideon.services.duplicate_detector import SmartDuplicateDetector
print('✓ All imports successful')
" || exit 1

# Test configuration
echo -e "\n3. Testing configuration..."
python3 -c "
from src.gideon.core.config import settings
print(f'✓ Config loaded')
print(f'  LLM Type: {settings.DEFAULT_LLM_SERVICE_TYPE}')
print(f'  LLM Model: {settings.DEFAULT_LLM_MODEL}')
" || exit 1

# Run unit tests
echo -e "\n4. Running unit tests..."
pytest tests/ -v --tb=short

echo -e "\n================================"
echo "Quick Test Complete!"
echo "================================"
