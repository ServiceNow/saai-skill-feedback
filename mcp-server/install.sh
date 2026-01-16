#!/bin/bash

# SAAI Skill Feedback - Installation Script
# Installs the feedback skill for Claude Desktop or Claude Code

set -e

echo ""
echo "=========================================="
echo "SAAI Skill Feedback - Installer"
echo "=========================================="
echo ""

# Get the absolute path to this script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Installation directory: $PROJECT_ROOT"
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo ""
    echo "Install Node.js first:"
    echo "  brew install node"
    echo ""
    exit 1
fi

echo "✓ Node.js found: $(node --version)"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo ""
    echo "Install Python 3 first:"
    echo "  brew install python3"
    echo ""
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd "$SCRIPT_DIR"
npm install
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --quiet selenium webdriver-manager requests 2>/dev/null || {
    echo "⚠️  Note: Some Python packages may already be installed"
}
echo ""

# Authenticate with ServiceNow
echo "=========================================="
echo "ServiceNow Authentication"
echo "=========================================="
echo ""
echo "Opening browser for ServiceNow authentication..."
echo "Please complete Okta login and MFA when prompted."
echo ""

python3 "$PROJECT_ROOT/src/utils/login_and_extract.py"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Authentication failed"
    echo ""
    echo "You can retry authentication later by running:"
    echo "  python3 $PROJECT_ROOT/src/utils/login_and_extract.py"
    echo ""
    exit 1
fi

echo ""
echo "=========================================="
echo "Claude Configuration"
echo "=========================================="
echo ""
echo "Add this to your Claude configuration:"
echo ""
echo "For Claude Desktop:"
echo "  File: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "For Claude Code:"
echo "  File: ~/.config/claude/config.json"
echo ""
echo "Add this entry to the 'mcpServers' section:"
echo ""
echo "{"
echo "  \"mcpServers\": {"
echo "    \"saai-skill-feedback\": {"
echo "      \"command\": \"node\","
echo "      \"args\": [\"$SCRIPT_DIR/index.js\"]"
echo "    }"
echo "  }"
echo "}"
echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Add the configuration above to your Claude config file"
echo "  2. Restart Claude Desktop or Claude Code"
echo "  3. Start a new conversation"
echo "  4. Test by saying: 'report a bug with <skill-name>'"
echo ""
echo "For help, see: $PROJECT_ROOT/docs/INSTALL.md"
echo ""
