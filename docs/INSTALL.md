# Installation Guide: SAAI Skill Feedback

Complete installation instructions for the feedback skill.

---

## Prerequisites

Before installing, make sure you have:

1. **Node.js 18+**
   ```bash
   node --version  # Should be 18.0.0 or higher
   ```
   Install: `brew install node`

2. **Python 3.8+**
   ```bash
   python3 --version  # Should be 3.8.0 or higher
   ```
   Install: `brew install python3`

3. **ServiceNow Access**
   - Account on https://surf.service-now.com
   - Able to create SBOs in the Security Data Analytics table

4. **Claude Desktop or Claude Code**
   - Claude Desktop: https://claude.ai/download
   - Claude Code: `npm install -g @anthropic/claude-code`

---

## Installation Steps

### Step 1: Download the Skill

**Option A: Git Clone** (if you have Git)
```bash
git clone https://github.com/yourusername/saai-skill-feedback.git
cd saai-skill-feedback
```

**Option B: Download ZIP**
1. Download ZIP from GitHub
2. Extract to a permanent location (NOT Downloads folder)
3. `cd saai-skill-feedback`

### Step 2: Run the Installer

```bash
cd mcp-server
./install.sh
```

The installer will:
1. Check for Node.js and Python
2. Install JavaScript dependencies (npm install)
3. Install Python dependencies (selenium, requests, etc.)
4. Open a browser for ServiceNow authentication
5. Save credentials to `~/.servicenow_surf_session.json`
6. Display configuration instructions

### Step 3: Authenticate with ServiceNow

During installation, a browser window will open:

1. **Log in to ServiceNow** (surf.service-now.com)
2. **Complete Okta authentication**
3. **Complete MFA** (push notification, SMS, etc.)
4. **Wait for confirmation** - Browser will close automatically
5. ✓ Credentials saved

**If authentication fails:**
```bash
# Retry authentication manually
python3 ../src/utils/login_and_extract.py
```

### Step 4: Configure Claude

The installer will show you the config to add. Copy the entire JSON block.

#### For Claude Desktop (macOS)

Config file location:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

1. Open the config file in a text editor
2. If the file doesn't exist, create it with:
   ```json
   {
     "mcpServers": {}
   }
   ```
3. Add the feedback skill to `mcpServers`:
   ```json
   {
     "mcpServers": {
       "saai-skill-feedback": {
         "command": "node",
         "args": ["/absolute/path/to/saai-skill-feedback/mcp-server/index.js"]
       }
     }
   }
   ```
4. **Replace `/absolute/path/to/` with the actual path** (shown by installer)
5. Save the file

#### For Claude Code

Config file location:
```
~/.config/claude/config.json
```

Same process as above, but use the Claude Code config file.

### Step 5: Restart Claude

**Claude Desktop:**
- Quit Claude completely (Cmd+Q)
- Relaunch Claude

**Claude Code:**
- Exit any running Claude Code sessions
- Restart Claude Code

### Step 6: Verify Installation

Start a new conversation in Claude and test:

```
Test message: "What tools do you have?"
```

You should see `submit_skill_feedback` listed in the tools.

---

## Testing the Skill

### Test 1: Basic Feedback

```
You: "Request a new skill for weather forecasts"

Claude: [Should ask for details and call submit_skill_feedback]
```

Expected output:
```
✓ Thank you for your feedback!
Feedback submitted successfully: DSRT0123456
[ServiceNow link]
```

### Test 2: Auto-Detection

First use another skill, then report feedback:

```
You: "Create an SBO for testing" (if you have create-sbo-request)
[SBO created]

You: "Report a bug - it was too slow"

Claude: [Should auto-detect skill_name="create-sbo-request"]
```

### Test 3: Check ServiceNow

1. Open the SBO link provided
2. Verify the details match what you submitted
3. Check assigned to "David Rider"
4. Work Activity should be "Platform Dev - Security BOS App"

---

## Troubleshooting

### Tool Not Showing Up

**Symptom**: Claude doesn't recognize `submit_skill_feedback`

**Solutions**:
1. **Restart Claude completely** - Not just close window, fully quit
2. **Start a NEW conversation** - Old conversations don't get new tools
3. **Check config file path**:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
4. **Verify path is absolute** - `/Users/you/...` not `~/...`
5. **Check for JSON syntax errors** - Missing comma, bracket, quote

### Authentication Errors

**Symptom**: "401 Unauthorized" or "Authentication failed"

**Solutions**:
1. **Re-authenticate**:
   ```bash
   python3 src/utils/login_and_extract.py
   ```
2. **Check credentials file exists**:
   ```bash
   ls -la ~/.servicenow_surf_session.json
   ```
3. **Verify ServiceNow access** - Try logging in manually at surf.service-now.com
4. **Clear and retry**:
   ```bash
   rm ~/.servicenow_surf_session.json
   python3 src/utils/login_and_extract.py
   ```

### Python Module Errors

**Symptom**: "ModuleNotFoundError: No module named 'selenium'"

**Solutions**:
```bash
# Install missing Python packages
pip3 install selenium webdriver-manager requests

# Or reinstall all dependencies
pip3 install -r requirements.txt
```

### Node.js Dependency Errors

**Symptom**: "Cannot find module '@modelcontextprotocol/sdk'"

**Solutions**:
```bash
cd mcp-server
rm -rf node_modules
npm install
```

### Browser Automation Issues

**Symptom**: Browser doesn't open or closes immediately

**Solutions**:

**For Chrome issues**:
```bash
# Install webdriver-manager
pip3 install webdriver-manager

# Chrome should auto-install, but if issues:
pip3 uninstall webdriver-manager
pip3 install webdriver-manager
```

**For Safari issues**:
```bash
# Enable Safari automation
sudo safaridriver --enable
```

**Try manual authentication**:
```bash
# Use Chrome (recommended)
python3 src/utils/login_and_extract.py --browser chrome

# Or use Safari
python3 src/utils/login_and_extract.py --browser safari
```

### MFA/Okta Issues

**Symptom**: "MFA detected - cannot complete authentication in headless mode"

**Solution**: The script should automatically use visible browser. If not:
```bash
# Force visible browser mode
python3 src/utils/login_and_extract.py
```

Never use `--headless` flag - MFA requires visible browser.

---

## Advanced Configuration

### Custom Python Path

If using a different Python version:

Edit `mcp-server/index.js` line ~50:
```javascript
const python = spawn('python3', args);
// Change to:
const python = spawn('/path/to/your/python', args);
```

### Environment Variables

Alternative to cached credentials:

```bash
export SNOW_X_USER_TOKEN="your-token-here"
export SNOW_COOKIE_GLIDE="your-glide-cookie"
export SNOW_COOKIE_SESSION="your-session-cookie"
```

Get these by running:
```bash
python3 src/utils/login_and_extract.py
```

They'll be printed at the end.

### Multiple ServiceNow Instances

To use with different ServiceNow instances:

1. Edit `src/utils/session_manager.py` line 17:
   ```python
   INSTANCE_URL = 'https://your-instance.service-now.com'
   ```

2. Edit `src/submit_feedback.py` line 26:
   ```python
   INSTANCE = "https://your-instance.service-now.com"
   ```

---

## Updating the Skill

### Pull Latest Changes

```bash
cd saai-skill-feedback
git pull origin main
cd mcp-server
npm install  # Update dependencies if needed
```

### Re-authenticate

If authentication expires:
```bash
python3 src/utils/login_and_extract.py
```

Credentials expire after ~24 hours and auto-refresh when needed.

---

## Uninstalling

### Remove from Claude Config

Edit your Claude config file and remove the `saai-skill-feedback` entry:

```json
{
  "mcpServers": {
    "saai-skill-feedback": { ... }  ← Remove this block
  }
}
```

### Remove Files

```bash
# Remove the skill
rm -rf /path/to/saai-skill-feedback

# Remove credentials (optional)
rm ~/.servicenow_surf_session.json
```

### Restart Claude

Quit and restart Claude to apply changes.

---

## Getting Help

**Installation issues?**
- Check this guide first
- Review error messages carefully
- Try the troubleshooting steps

**Still stuck?**
- Contact David Rider
- Include error messages and OS version
- Mention which step failed

**Found a bug?**
- Use the feedback skill to report it! (meta)
- Or file an issue on GitHub

---

## Next Steps

After successful installation:

1. **Test the skill** - Try each feedback type
2. **Check ServiceNow** - Verify SBOs are created correctly
3. **Share with team** - See [TEAM_MESSAGE.md](TEAM_MESSAGE.md)
4. **Start using it** - Report bugs and enhancements as you work

---

## Security Notes

### Credentials

- Stored at `~/.servicenow_surf_session.json`
- Contains cookies and X-UserToken
- Auto-refreshes when expired
- File permissions: `600` (your user only)

### Network

- Connects only to surf.service-now.com
- Uses HTTPS for all API calls
- No telemetry or external tracking

### Browser Automation

- Opens Chrome/Safari for authentication
- Runs locally on your machine
- No credentials sent to third parties
- Browser closes after authentication

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Node.js | 18.0.0 | Latest LTS |
| Python | 3.8.0 | 3.11+ |
| RAM | 4 GB | 8 GB+ |
| Disk | 100 MB | 500 MB |
| OS | macOS 12+ | macOS 14+ |

Also compatible with Linux. Windows support via WSL.

---

## FAQ

**Q: Do I need admin access to install?**
A: No, installs in user directory. No sudo required.

**Q: Can I install multiple MCP skills?**
A: Yes! Add each to the `mcpServers` config section.

**Q: How often do credentials expire?**
A: ~24 hours, but auto-refresh automatically.

**Q: Can I use this with Claude API?**
A: No, this is for Claude Desktop/Code only (MCP protocol).

**Q: Is this official from ServiceNow/Anthropic?**
A: No, internal tool by Security Analytics team.

**Q: Can I customize the feedback types?**
A: Yes, edit `src/submit_feedback.py` EMOJI_MAP.

**Q: Where are SBOs created?**
A: surf.service-now.com table `x_snc_security_d_0_dsrtable`

**Q: Who gets the feedback?**
A: Assigned to David Rider (skill maintainer).

---

## Appendix: Manual Configuration

If the installer fails, configure manually:

### 1. Install Node Dependencies
```bash
cd mcp-server
npm install @modelcontextprotocol/sdk zod
```

### 2. Install Python Dependencies
```bash
pip3 install selenium webdriver-manager requests
```

### 3. Authenticate
```bash
python3 src/utils/login_and_extract.py
```

### 4. Add to Claude Config
Use the config shown earlier in this guide.

### 5. Restart Claude
Quit and relaunch.

---

For more information, see:
- [README.md](../README.md) - Overview
- [CLAUDE.md](CLAUDE.md) - Instructions for Claude
- [TEAM_MESSAGE.md](TEAM_MESSAGE.md) - Team distribution