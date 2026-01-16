# Claude Instructions: SAAI Skill Feedback

## Purpose

This skill allows users to submit feedback about ANY MCP skill they use with Claude. It creates ServiceNow SBOs with full conversation context.

## When to Use This Tool

Use `submit_skill_feedback` when the user:

1. **Reports a bug**: "report a bug", "found a bug", "something's broken", "not working", "error"
2. **Requests an enhancement**: "request enhancement", "improve this", "add feature", "make it better"
3. **Requests a new skill**: "request new skill", "need a different skill", "create a skill for X"

## How to Use the Tool

### Step 1: Auto-Detect Skill Name

Look back through the conversation history (last 10-15 messages) to identify which MCP skill the user was using:

- Look for tool calls like `create_sbo_request`, `submit_feedback`, etc.
- Extract the skill name from the tool name (e.g., "create-sbo-request" from "create_sbo_request")
- If multiple skills were used, choose the MOST RECENT one
- If no skill detected, ask the user: "Which skill are you reporting feedback about?"

**Examples**:
```
User: "The create-sbo-request tool didn't find my dashboard"
→ skill_name = "create-sbo-request" (from recent tool use)

User: "Request a new skill for managing Jira tickets"
→ skill_name = null (this is a new skill request)
```

### Step 2: Capture Conversation Context

Extract 3-5 relevant messages that show the issue:

- For **bugs**: Include the tool call, parameters, error message, and user's description
- For **enhancements**: Include current behavior and what user wants instead
- For **new skills**: Include the use case and requirements

Format the context as a clear narrative:

```
**Recent Interaction:**

User requested: "Create an SBO for updating the security dashboard"

Tool call: create_sbo_request
Parameters: {
  "title": "Update security dashboard",
  "description": "..."
}

Tool response: "✗ Error: Dashboard 'security' not found in mapping..."

User feedback: "The dashboard lookup didn't work - it should find partial matches"
```

### Step 3: Enrich the Message

Build a comprehensive feedback message by combining:

1. **User's original feedback** (their exact words)
2. **Technical details** (error messages, tool parameters, responses)
3. **Expected vs actual behavior** (what should happen vs what happened)
4. **Relevant context** (what they were trying to do)

**Example for a bug report**:
```
Original message: "The dashboard lookup didn't work"

Enriched message:
"The create-sbo-request tool failed to find the dashboard when given 'security' as the name.

Expected behavior: The tool should match 'security' to 'Security Scorecard' dashboard (partial matching).

Actual behavior: Tool returned error 'Dashboard not found' and didn't create the SBO.

Tool parameters used:
- title: "Update security dashboard"
- related_dashboard: "security"

The user expected fuzzy matching on dashboard names similar to how work activity detection works."
```

### Step 4: Call the Tool

Call `submit_skill_feedback` with:

- `feedback_type`: Choose "bug", "enhancement", or "new_skill"
- `message`: The enriched message from Step 3
- `skill_name`: Auto-detected skill name (or null for new_skill)
- `conversation_context`: The formatted context from Step 2

### Step 5: Confirm Submission

After successful submission, tell the user:

```
✓ Thank you for your feedback! I've reported this {bug/enhancement/request} to the team.

The feedback has been submitted as SBO {number} and will be reviewed by the skill maintainer.

{link}
```

## Critical Rules

### Rule 1: ALWAYS Include Context

Never submit feedback without conversation context. Users often say just "report a bug" but you MUST:
- Look back at what happened
- Extract relevant tool calls and responses
- Include this in the message

### Rule 2: Enrich Bug Reports

For bugs, ALWAYS include:
- What the user was trying to do
- What parameters/inputs they provided
- The error message or unexpected behavior
- What they expected to happen

### Rule 3: Enrich Enhancement Requests

For enhancements, ALWAYS include:
- Current behavior (what happens now)
- Desired behavior (what should happen)
- Use case (why this would be useful)
- Examples if provided

### Rule 4: Enrich New Skill Requests

For new skill requests, ALWAYS include:
- What task the user wants to accomplish
- Why existing skills don't meet the need
- Expected functionality and use cases
- Any technical requirements mentioned

### Rule 5: Auto-Detection

ALWAYS attempt to auto-detect the skill name from conversation:
- Scan last 10-15 messages for tool calls
- Extract skill name from tool name
- Only ask user if truly ambiguous

### Rule 6: Be Proactive

When you see users struggling with a skill, OFFER to submit feedback:
```
"I notice the dashboard lookup isn't working as expected. Would you like me to report this bug to the team?"
```

Don't wait for them to explicitly say "report a bug" - be helpful!

## Feedback Types

### Bug Reports

**Indicators**: "broken", "not working", "error", "failed", "issue"

**Required information**:
- Exact error message
- Tool parameters used
- Expected vs actual behavior
- Steps to reproduce

**Example**:
```
feedback_type: "bug"
message: "The create_sbo_request tool throws an error when assigned_to is set to 'Lotenna'.

Error: 'User not found'

Expected: Should recognize 'Lotenna' and map to 'Lotenna Nwana' (full name in ServiceNow)

Steps to reproduce:
1. Call create_sbo_request with assigned_to: 'Lotenna'
2. Tool returns error instead of creating SBO

The tool should support first name lookups like it does for 'David' → 'David Rider'."

skill_name: "create-sbo-request"
conversation_context: "[relevant tool call and response]"
```

### Enhancement Requests

**Indicators**: "improve", "add", "support", "would be nice", "suggestion"

**Required information**:
- Current limitation
- Proposed improvement
- Use case
- Benefits

**Example**:
```
feedback_type: "enhancement"
message: "Add support for due date ranges in create_sbo_request.

Current: Can only specify single due date (YYYY-MM-DD)
Proposed: Allow ranges like 'within 2 weeks' or 'between Jan 15-30'

Use case: Often users know the timeframe but not exact date. Having flexible due date input would make the tool more natural to use.

Example inputs:
- 'within 2 weeks'
- 'by end of month'
- 'Q1 2026'

This would be processed into the earliest reasonable due date within that range."

skill_name: "create-sbo-request"
```

### New Skill Requests

**Indicators**: "need a skill for", "create a tool that", "wish there was a skill"

**Required information**:
- What task needs to be accomplished
- Why existing skills don't work
- Expected functionality
- Use cases

**Example**:
```
feedback_type: "new_skill"
message: "Request for a Jira ticket management skill for Claude.

Use case: Our team uses Jira for sprint planning and bug tracking. Would be helpful to create, update, and query Jira tickets directly from Claude conversations.

Desired functionality:
- Create Jira tickets with title, description, assignee, labels
- Query tickets by JQL or filters
- Update ticket status and fields
- Add comments to tickets
- Link to ServiceNow SBOs (nice to have)

Why needed: Currently have to switch to Jira UI, breaking flow. Having Claude integration would streamline sprint planning and bug triage.

Technical notes:
- Jira Cloud API is well documented
- Could use OAuth or API tokens for auth
- Similar pattern to create-sbo-request skill"

skill_name: null
```

## Example Interactions

### Example 1: Bug Report

```
User: "Create an SBO for fixing the security dashboard"

[Tool: create_sbo_request called]

Tool response: "✗ Error: Dashboard 'security' not found"

User: "That's annoying, it should find it"

Claude: "I agree - the dashboard lookup should be more flexible. Would you like me to report this as a bug?"

User: "Yes please"

Claude: [Calls submit_skill_feedback]
- feedback_type: "bug"
- skill_name: "create-sbo-request" (auto-detected)
- message: "Dashboard lookup fails for partial names. When user provided 'security' as the dashboard name, the tool returned 'Dashboard not found' error instead of matching it to 'Security Scorecard'. The tool should support partial matching on dashboard names similar to how it handles work activity detection. User was trying to create an SBO for dashboard maintenance but was blocked by strict name matching."
- conversation_context: "User requested: 'Create an SBO for fixing the security dashboard'\n\nTool: create_sbo_request\nParameters: {title: 'Fix security dashboard', related_dashboard: 'security'}\nResponse: Error - Dashboard 'security' not found\n\nUser feedback: 'That's annoying, it should find it'"

Claude: "✓ Thank you for your feedback! I've reported this bug to the team. The feedback has been submitted as SBO DSRT0123456..."
```

### Example 2: Enhancement Request

```
User: "Create 3 SBOs - one for Lotenna, one for Aparna, and one for Tim"

Claude: "I'll create those SBOs for you..."
[Creates 3 separate SBOs]

User: "That worked but it would be better if the tool could create multiple in one call"

Claude: "That's a great suggestion! Would you like me to submit this as an enhancement request?"

User: "Sure"

Claude: [Calls submit_skill_feedback]
- feedback_type: "enhancement"
- skill_name: "create-sbo-request" (auto-detected)
- message: "Add support for batch SBO creation in a single tool call. Currently, creating multiple SBOs requires multiple separate create_sbo_request calls. User suggests adding support for passing arrays of SBO requests. Example: Instead of 3 separate calls, allow: {requests: [{title: '...', assigned_to: 'Lotenna'}, {title: '...', assigned_to: 'Aparna'}, ...]}\n\nBenefits: Faster workflow, fewer API calls, atomic operation (all succeed or all fail), better for sprint planning sessions where multiple tickets are created at once."
- conversation_context: "[relevant conversation showing 3 separate tool calls]"
```

### Example 3: New Skill Request

```
User: "I wish I could query our Snowflake database from Claude"

Claude: "That would be useful! I don't currently have a skill for direct Snowflake queries. Would you like me to submit a request for a new skill?"

User: "Yes, that would be great"

Claude: [Calls submit_skill_feedback]
- feedback_type: "new_skill"
- skill_name: null (new skill request)
- message: "Request for a Snowflake query skill for Claude.\n\nUse case: User wants to query the team's Snowflake database directly from Claude conversations to pull data for analysis, reporting, and answering questions.\n\nDesired functionality:\n- Execute SQL queries against Snowflake\n- Return results in readable format (tables, JSON, CSV)\n- Support for parameterized queries\n- Query history and result caching\n- Read-only access for safety\n\nWhy needed: Currently users must switch to Snowflake UI to run queries, breaking the flow of conversation. Having Claude integration would enable data-driven discussions without context switching.\n\nTechnical considerations:\n- Snowflake has Python connector and REST API\n- OAuth or API key authentication\n- Need to limit query complexity/runtime for safety\n- Should support connection to multiple Snowflake databases"
- conversation_context: "User: 'I wish I could query our Snowflake database from Claude'\nClaude: 'I don't currently have access to Snowflake...'"
```

## Edge Cases

### Multiple Skills in Conversation

If user has used multiple skills recently, use the MOST RECENT one:

```
[Earlier: used create-sbo-request]
[More recent: used some-other-skill]

User: "report a bug"

→ skill_name = "some-other-skill" (most recent)
```

### Ambiguous Skill Name

If truly ambiguous, ask the user:

```
Claude: "I see you've used both create-sbo-request and analytics-query recently. Which skill are you reporting feedback about?"
```

### No Skill Detected

For new skill requests, this is expected:

```
User: "Request a skill for managing GitHub PRs"

→ skill_name = null (this is a new skill request, not feedback about existing skill)
```

### User Specifies Skill Explicitly

If user mentions skill name, use it:

```
User: "Report a bug with create-sbo-request"

→ skill_name = "create-sbo-request" (explicitly stated)
```

## Quality Guidelines

### High-Quality Feedback

✓ Includes specific error messages
✓ Shows what user was trying to do
✓ Explains expected vs actual behavior
✓ Provides reproduction steps
✓ Captures relevant conversation context

### Low-Quality Feedback (Avoid)

✗ "Something is broken"
✗ No context about what happened
✗ No error messages or details
✗ Can't tell what user was trying to do

Always enrich the feedback before submission!

## Testing

After implementing this skill, test with:

1. Bug report after failed tool call
2. Enhancement request during successful workflow
3. New skill request without recent tool usage
4. Multiple skills used - verify correct detection
5. Explicit skill name in user message

## Notes

- This skill works with ANY MCP skill, not just ones we maintain
- Auto-detection makes it easy for users to report feedback
- Rich context ensures maintainers can act on feedback quickly
- All feedback routes to David Rider as skill ecosystem owner