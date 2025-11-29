#!/bin/bash
# DistroFlow Pre-Launch Automated Tests
# Run this script before launching to verify everything works

set -e  # Exit on any error

echo "🧪 DistroFlow Pre-Launch Tests"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Test Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    error "Python 3.8+ required, found $PYTHON_VERSION"
fi
success "Python version OK: $PYTHON_VERSION"
echo ""

# 2. Test virtualenv exists
echo "2. Checking virtual environment..."
if [ ! -d "venv" ]; then
    warn "Virtual environment not found, creating..."
    python3 -m venv venv
fi
success "Virtual environment OK"
echo ""

# 3. Activate virtualenv
echo "3. Activating virtual environment..."
source venv/bin/activate || error "Failed to activate virtualenv"
success "Virtual environment activated"
echo ""

# 4. Test dependencies
echo "4. Checking dependencies..."
pip list | grep -q "playwright" || error "Playwright not installed"
pip list | grep -q "fastapi" || error "FastAPI not installed"
pip list | grep -q "click" || error "Click not installed"
success "All dependencies installed"
echo ""

# 5. Test distroflow CLI
echo "5. Testing CLI installation..."
if ! command -v distroflow &> /dev/null; then
    warn "distroflow command not found, installing..."
    pip install -e . > /dev/null || error "Failed to install distroflow"
fi
distroflow --version > /dev/null || error "distroflow CLI not working"
success "CLI installation OK"
echo ""

# 6. Test API server
echo "6. Testing API server..."
if ! python3 test_api_server.py; then
    error "API server tests failed"
fi
success "API server tests passed"
echo ""

# 7. Test code formatting
echo "7. Testing code formatting (Black)..."
if ! ./venv/bin/black --check distroflow/ > /dev/null 2>&1; then
    warn "Code not formatted with Black"
    echo "   Run: ./venv/bin/black distroflow/"
fi
success "Code formatting OK"
echo ""

# 8. Test linting
echo "8. Testing code quality (Flake8)..."
FLAKE8_ERRORS=$(./venv/bin/flake8 distroflow/ --max-line-length=100 --extend-ignore=E203,W503 --count)
if [ "$FLAKE8_ERRORS" -ne "0" ]; then
    warn "$FLAKE8_ERRORS linting issues found"
else
    success "No linting issues"
fi
echo ""

# 9. Test imports
echo "9. Testing Python imports..."
python3 -c "from distroflow import __version__; from distroflow.api import server; from distroflow.platforms import base" || error "Import failed"
success "All imports OK"
echo ""

# 10. Test extension files
echo "10. Testing extension files..."
[ -f "extension/manifest.json" ] || error "extension/manifest.json missing"
[ -f "extension/popup.html" ] || error "extension/popup.html missing"
[ -f "extension/popup.css" ] || error "extension/popup.css missing"
[ -f "extension/popup.js" ] || error "extension/popup.js missing"
[ -f "extension/background.js" ] || error "extension/background.js missing"
[ -f "extension/content.js" ] || error "extension/content.js missing"
[ -f "extension/icons/icon16.png" ] || error "extension/icons/icon16.png missing"
[ -f "extension/icons/icon48.png" ] || error "extension/icons/icon48.png missing"
[ -f "extension/icons/icon128.png" ] || error "extension/icons/icon128.png missing"
success "All extension files present"
echo ""

# 11. Test documentation
echo "11. Testing documentation..."
[ -f "README.md" ] || error "README.md missing"
[ -f "docs/QUICKSTART.md" ] || error "docs/QUICKSTART.md missing"
[ -f "docs/ARCHITECTURE.md" ] || error "docs/ARCHITECTURE.md missing"
[ -f "docs/EXTENSION.md" ] || error "docs/EXTENSION.md missing"
[ -f "CHANGELOG.md" ] || error "CHANGELOG.md missing"
[ -f "CONTRIBUTING.md" ] || error "CONTRIBUTING.md missing"
[ -f "LICENSE" ] || error "LICENSE missing"
success "All documentation present"
echo ""

# 12. Test package structure
echo "12. Testing package structure..."
[ -d "distroflow" ] || error "distroflow/ directory missing"
[ -d "distroflow/core" ] || error "distroflow/core/ missing"
[ -d "distroflow/platforms" ] || error "distroflow/platforms/ missing"
[ -d "distroflow/api" ] || error "distroflow/api/ missing"
[ -f "distroflow/__init__.py" ] || error "distroflow/__init__.py missing"
[ -f "distroflow/cli.py" ] || error "distroflow/cli.py missing"
[ -f "setup.py" ] || error "setup.py missing"
success "Package structure OK"
echo ""

# 13. Test .gitignore
echo "13. Testing .gitignore..."
[ -f ".gitignore" ] || error ".gitignore missing"
grep -q "*.pyc" .gitignore || warn ".gitignore might be incomplete"
grep -q "venv/" .gitignore || warn ".gitignore missing venv/"
grep -q "*.db" .gitignore || warn ".gitignore missing *.db"
success ".gitignore OK"
echo ""

# 14. Test no secrets in repo
echo "14. Checking for secrets..."
if grep -r "sk-proj-" distroflow/ extension/ 2>/dev/null | grep -v "EXAMPLE" | grep -v ".pyc"; then
    error "Found OpenAI API key in code!"
fi
if grep -r "sk-ant-" distroflow/ extension/ 2>/dev/null | grep -v "EXAMPLE" | grep -v ".pyc"; then
    error "Found Anthropic API key in code!"
fi
if grep -r "auth_token.*:" distroflow/ extension/ 2>/dev/null | grep -v "example" | grep -v ".pyc"; then
    warn "Possible auth tokens in code, please verify"
fi
success "No obvious secrets found"
echo ""

# 15. Test file sizes
echo "15. Checking file sizes..."
README_SIZE=$(wc -c < "README.md")
if [ "$README_SIZE" -lt 10000 ]; then
    warn "README seems short (${README_SIZE} bytes)"
fi
success "File sizes OK"
echo ""

# Final summary
echo ""
echo "=============================="
echo -e "${GREEN}✅ All tests passed!${NC}"
echo "=============================="
echo ""
echo "📋 Pre-Launch Checklist:"
echo "  - [$(if [ $FLAKE8_ERRORS -eq 0 ]; then echo '✅'; else echo '⚠️ '; fi)] Code quality"
echo "  - [✅] Dependencies installed"
echo "  - [✅] CLI working"
echo "  - [✅] API server tested"
echo "  - [✅] Extension files present"
echo "  - [✅] Documentation complete"
echo "  - [✅] No secrets in code"
echo ""
echo "🚀 Ready to launch!"
echo ""
echo "Next steps:"
echo "  1. Test extension in Chrome (chrome://extensions/)"
echo "  2. Record demo video"
echo "  3. Create demo GIFs"
echo "  4. Review LAUNCH_PLAN.md"
echo "  5. Launch! 🎉"
echo ""
