# Team Distribution: SAAI Skill Feedback

Templates for announcing the feedback skill to your team.

---

## Email Template

**Subject:** New Tool: Submit Feedback for Claude Skills

Hi team,

I've created a new Claude skill that makes it easy to report bugs, request enhancements, or propose new skills - all directly from your Claude conversations.

**What is it?**
A feedback tool that:
- Auto-detects which skill you're using
- Captures conversation context automatically
- Creates ServiceNow SBOs with all the details
- Routes feedback to me for review

**How to use it:**
Just say things like:
- "Report a bug with create-sbo-request"
- "Request an enhancement - support date ranges"
- "Request a new skill for Jira management"

Claude will handle the rest!

**Installation:**
1. Download from: [OneDrive link]
2. Run: `cd saai-skill-feedback/mcp-server && ./install.sh`
3. Follow the prompts
4. Restart Claude

Full instructions: See INSTALL.md in the download

**Why use this?**
- Faster than filing tickets manually
- Captures technical details automatically
- Helps me improve our tools
- All feedback tracked in ServiceNow

Questions? Reach out to me directly.

Thanks,
[Your name]

---

## Slack Message Template

```
🆕 New Claude Skill: SAAI Skill Feedback

Submit bugs, enhancements, and new skill requests directly from Claude conversations!

✨ Features:
• Auto-detects which skill from conversation
• Captures context automatically
• Creates ServiceNow SBOs
• Routes to skill maintainer

📥 Installation:
1. Download: [link]
2. Run install.sh
3. Restart Claude
4. Start using!

📖 Docs: See INSTALL.md in download

💬 Usage examples:
• "Report a bug - dashboard lookup failed"
• "Request enhancement - add fuzzy matching"
• "Request a new skill for Snowflake queries"

Questions? DM me!
```

---

## Quick Start Card

```
┌─────────────────────────────────────────┐
│    SAAI SKILL FEEDBACK - QUICK START    │
├─────────────────────────────────────────┤
│                                         │
│  📥 INSTALL                             │
│  1. Download from [link]                │
│  2. cd saai-skill-feedback/mcp-server   │
│  3. ./install.sh                        │
│  4. Restart Claude                      │
│                                         │
│  💬 USE IT                              │
│  • "Report a bug with [skill]"          │
│  • "Request enhancement - [idea]"       │
│  • "Request new skill for [purpose]"    │
│                                         │
│  🎯 WHAT IT DOES                        │
│  ✓ Auto-detects skill from conversation │
│  ✓ Captures context automatically       │
│  ✓ Creates ServiceNow SBO               │
│  ✓ Routes to maintainer                 │
│                                         │
│  📖 Help: INSTALL.md in download        │
│                                         │
└─────────────────────────────────────────┘
```

---

## OneDrive Setup

### Create Shareable Link

1. **Upload folder to OneDrive**:
   ```
   saai-skill-feedback/
   ├── mcp-server/
   ├── src/
   ├── docs/
   ├── README.md
   └── LICENSE
   ```

2. **Right-click** → **Share** → **Anyone with the link**

3. **Copy link** for distribution

### Alternative: GitHub Release

If using GitHub:

1. Create release tag:
   ```bash
   git tag -a v1.0.0 -m "Initial release"
   git push origin v1.0.0
   ```

2. Create GitHub release with ZIP download

3. Share release URL

---

## FAQ for Team

**Q: Do I need to install this if I already have create-sbo-request?**
A: Yes! The feedback system was removed from create-sbo-request and is now a separate skill. Install it if you want to provide feedback.

**Q: Will this work with all MCP skills?**
A: Yes! It works with any MCP skill, not just ones we've created.

**Q: Who sees my feedback?**
A: All feedback goes to David Rider as ServiceNow SBOs.

**Q: Do I need ServiceNow access?**
A: Yes, you'll authenticate with surf.service-now.com during installation.

**Q: How often do I need to re-authenticate?**
A: Credentials last ~24 hours and auto-refresh when needed.

**Q: Can I test this first?**
A: Yes! After installing, try: "Request a new skill for weather forecasts" to test.

**Q: What if I don't want to install it?**
A: No problem! It's optional. You can still give feedback directly via Slack/email.

---

## Rollout Tips

### Phased Rollout

**Week 1: Early Adopters**
- Distribute to 2-3 power users
- Gather feedback on installation
- Fix any issues

**Week 2: Team-Wide**
- Send to full team
- Include installation help session
- Monitor adoption

**Week 3: Follow-Up**
- Check usage metrics
- Answer questions
- Share success stories

### Installation Help Session

Schedule 30-min session to help team install:

**Agenda:**
1. Demo the feedback skill (5 min)
2. Walk through installation (10 min)
3. Test it together (5 min)
4. Q&A (10 min)

**Materials needed:**
- Screen share setup
- OneDrive link ready
- Test ServiceNow access
- Backup troubleshooting doc

---

## Success Metrics

Track adoption:
- Number of installs
- Number of feedback SBOs created
- Types of feedback (bug vs enhancement vs new skill)
- Time from issue to feedback submission

Measure impact:
- Faster feedback loop
- More detailed bug reports
- Better feature requests
- Higher team engagement

---

## Support Plan

**Installation Issues:**
- First line: INSTALL.md troubleshooting section
- Second line: 1-on-1 help from you
- Escalation: Re-check authentication setup

**Usage Questions:**
- Reference: docs/CLAUDE.md
- Examples: README.md
- Help channel: [Slack channel name]

**Bug Reports:**
- Use the feedback skill itself! (meta)
- Or file GitHub issues
- Or reach out directly

---

## Communication Schedule

**Day 1: Announcement**
- Send email/Slack with overview
- Include installation link
- Set expectations for support

**Day 3: Reminder**
- Follow up with non-installers
- Share early success stories
- Offer help session

**Week 2: Check-In**
- Survey users on experience
- Address common issues
- Gather improvement ideas

**Monthly: Updates**
- Share usage stats
- Highlight great feedback received
- Announce improvements made

---

## Templates for Follow-Up

### Installation Reminder (Day 3)

```
Quick reminder: Have you installed the SAAI Skill Feedback tool yet?

It takes 5 minutes and makes it super easy to report bugs or request features.

Download: [link]
Help: Reach out if you run into issues!
```

### Success Story Share

```
🎉 Thanks to [Name] for reporting a bug via the feedback skill!

They noticed the dashboard lookup wasn't working and submitted feedback with full context. We've already fixed it and released an update.

This is exactly how the feedback loop should work - quick, easy, and effective!

Haven't installed yet? Get it here: [link]
```

### Monthly Update

```
📊 Feedback Skill Stats - January 2026

✓ 15 team members using it
✓ 23 pieces of feedback received
✓ 8 bugs fixed
✓ 5 enhancements implemented
✓ 2 new skills in development

Top feedback this month:
1. Dashboard fuzzy matching (✓ shipped!)
2. Batch SBO creation (in progress)
3. Jira integration skill (planned)

Keep the feedback coming! Every submission helps improve our tools.
```

---

## GitHub README Badge

If using GitHub, add badge to README:

```markdown
[![Feedback Welcome](https://img.shields.io/badge/feedback-welcome-brightgreen.svg)](mailto:your.email@company.com)
```

Or create custom badge:
```markdown
[![Submit Feedback](https://img.shields.io/badge/💬-submit%20feedback-blue.svg)](#installation)
```

---

## Related Documentation

- [README.md](../README.md) - Skill overview
- [INSTALL.md](INSTALL.md) - Installation guide
- [CLAUDE.md](CLAUDE.md) - Claude instructions

---

## Questions?

Contact: David Rider
Email: [your email]
Slack: @david.rider

Feedback about the feedback skill? Use the feedback skill! 😄