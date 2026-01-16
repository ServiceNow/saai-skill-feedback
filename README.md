# SAAI Skill Feedback

Submit feedback about Claude MCP skills directly from your conversations.

Report bugs, request enhancements, or propose new skills - all tracked in ServiceNow SBOs with full conversation context.

---

## Quick Start

### Install

```bash
git clone https://github.com/ServiceNow/saai-skill-feedback.git
cd saai-skill-feedback/mcp-server
./install.sh
```

### Use It

Just tell Claude:

```
"Report a bug with create-sbo-request"
"Request an enhancement to make dashboard lookups fuzzy"
"Request a new skill for Jira ticket management"
```

Claude will auto-detect which skill you're talking about and submit the feedback with full context.

---

## What This Does

Instead of manually filing bug reports or feature requests, just mention it in your Claude conversation:

- **Auto-detects** which skill from conversation history
- **Captures context** automatically (tool calls, errors, parameters)
- **Enriches feedback** with technical details
- **Creates SBOs** in ServiceNow for tracking
- **Assigns to maintainer** automatically

---

## Features

### Bug Reports

When something doesn't work, just say:
```
"Report a bug - the dashboard lookup failed"
```

Claude will:
- Find which tool was called
- Extract the error message
- Capture parameters used
- Create SBO with all details

### Enhancement Requests

When you want improvements:
```
"Request enhancement - support partial dashboard names"
```

Claude will:
- Describe current behavior
- Explain desired behavior
- Capture use case
- Submit enhancement request

### New Skill Requests

When you need something new:
```
"Request a skill for Jira ticket management"
```

Claude will:
- Capture the use case
- Extract requirements
- Create new skill request SBO

---

## Installation

See [docs/INSTALL.md](docs/INSTALL.md) for detailed setup instructions.

**Requirements**:
- Node.js 18+
- Python 3.8+
- ServiceNow account (surf.service-now.com)

**Quick install**:
```bash
cd mcp-server
./install.sh
```

This will:
1. Install Node.js and Python dependencies
2. Authenticate with ServiceNow (browser-based)
3. Show you the config to add to Claude

---

## Configuration

Add to your Claude config file:

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
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

**Claude Code** (`~/.config/claude/config.json`):
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

---

## How It Works

### Auto-Detection

When you say "report a bug", Claude:
1. Scans recent conversation (last 10-15 messages)
2. Finds the last MCP tool call
3. Extracts the skill name
4. Captures relevant context

### Context Capture

For bug reports, captures:
- Tool name and parameters
- Error messages
- Expected vs actual behavior
- User's description

For enhancements:
- Current limitation
- Desired improvement
- Use case and benefits

For new skills:
- Problem to solve
- Expected functionality
- Why existing skills don't work

### SBO Creation

Creates ServiceNow SBO with:
- Title: "{emoji} {type}: {skill_name}"
- Description: Full feedback with context
- Work Activity: "Platform Dev - Security BOS App"
- Assigned to: David Rider (skill maintainer)
- State: Opened

---

## Examples

### Bug Report
```
User: "Create an SBO for fixing the security dashboard"
[Tool error: Dashboard not found]
User: "Report a bug - it should find partial matches"

Claude: [Auto-detects skill_name="create-sbo-request"]
Claude: [Captures error and parameters]
Claude: [Submits SBO with enriched context]
Claude: "✓ Feedback submitted as SBO DSRT0123456"
```

### Enhancement Request
```
User: "It would be great if the tool supported date ranges"
Claude: "Would you like me to submit that as an enhancement?"
User: "Yes"

Claude: [Detects skill from recent usage]
Claude: [Captures current behavior vs desired]
Claude: [Submits enhancement SBO]
```

### New Skill Request
```
User: "I wish I could query Snowflake from Claude"
Claude: "I don't have that capability. Want me to request a new skill?"
User: "Please"

Claude: [No skill detection needed - it's a new skill]
Claude: [Captures use case and requirements]
Claude: [Submits new skill request SBO]
```

---

## Documentation

- **[docs/CLAUDE.md](docs/CLAUDE.md)** - Detailed Claude instructions
- **[docs/INSTALL.md](docs/INSTALL.md)** - Installation guide
- **[docs/TEAM_MESSAGE.md](docs/TEAM_MESSAGE.md)** - How to roll out to your team

---

## Feedback Types

| Type | When to Use | Example |
|------|------------|---------|
| **bug** | Something is broken | Dashboard lookup fails, tool returns error |
| **enhancement** | Improve existing feature | Add fuzzy matching, support date ranges |
| **new_skill** | Need new functionality | Jira integration, Snowflake queries |

---

## ServiceNow Details

- **Instance**: https://surf.service-now.com
- **Table**: `x_snc_security_d_0_dsrtable` (Security BOS)
- **Assignee**: David Rider (skill maintainer)
- **Work Activity**: Platform Dev - Security BOS App

All feedback is tracked as standard SBO requests in ServiceNow.

---

## Authentication

Uses the same browser-based authentication as other ServiceNow skills:

1. Run install script
2. Browser opens for Okta login
3. Complete MFA
4. Credentials cached at `~/.servicenow_surf_session.json`
5. Auto-refreshes when expired

See [docs/INSTALL.md](docs/INSTALL.md) for authentication details.

---

## Troubleshooting

**Tool not showing up?**
- Restart Claude completely
- Start a NEW conversation
- Check config file path is absolute (not relative)

**Authentication errors?**
- Re-run: `python3 src/utils/login_and_extract.py`
- Complete browser login
- Check credentials: `ls -la ~/.servicenow_surf_session.json`

**Can't detect skill?**
- Mention skill explicitly: "report a bug with create-sbo-request"
- Claude will ask if truly ambiguous

---

## For Developers

### Project Structure
```
saai-skill-feedback/
├── mcp-server/
│   ├── index.js          # MCP server entry point
│   ├── package.json      # Node dependencies
│   └── install.sh        # Installer script
├── src/
│   ├── submit_feedback.py           # Feedback submission logic
│   └── utils/
│       ├── session_manager.py       # ServiceNow auth
│       └── login_and_extract.py     # Browser automation
└── docs/
    ├── CLAUDE.md         # Instructions for Claude
    ├── INSTALL.md        # User installation guide
    └── TEAM_MESSAGE.md   # Rollout templates
```

### Tech Stack
- **Node.js**: MCP server using @modelcontextprotocol/sdk
- **Python**: ServiceNow API integration
- **Selenium**: Browser automation for auth
- **ServiceNow REST API**: SBO creation

### Adding Support for New Feedback Types

Edit `src/submit_feedback.py`:
```python
EMOJI_MAP = {
    'bug': '🐛',
    'enhancement': '✨',
    'new_skill': '💡',
    'your_new_type': '🎯',  # Add here
}
```

---

## Contributing

Feedback about the feedback skill? Report it using the feedback skill! (meta)

Or submit issues/PRs on GitHub.

---

## License

MIT License - See LICENSE file

---

## Credits

Built by the Security Analytics team at ServiceNow.

Uses the Model Context Protocol (MCP) from Anthropic.