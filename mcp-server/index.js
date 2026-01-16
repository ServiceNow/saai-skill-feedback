#!/usr/bin/env node

/**
 * SAAI Skill Feedback MCP Server
 *
 * Allows users to submit feedback about any MCP skill they use.
 * Auto-detects which skill from conversation context.
 *
 * Features:
 *   - Report bugs
 *   - Request enhancements
 *   - Request new skills
 *   - Auto-detect skill name from conversation
 *   - Capture conversation context automatically
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Schema for tool input validation
const SubmitFeedbackSchema = z.object({
  feedback_type: z.enum(['bug', 'enhancement', 'new_skill']).describe("Type of feedback"),
  message: z.string().describe("Detailed feedback message"),
  skill_name: z.string().optional().describe("Name of the skill (auto-detected if not provided)"),
  conversation_context: z.string().optional().describe("Relevant conversation excerpt"),
});

/**
 * Submit feedback by calling the Python script
 */
async function submitFeedback(params) {
  // Build Python script path
  const scriptPath = path.resolve(__dirname, '../src/submit_feedback.py');

  // Build command arguments
  const args = [
    scriptPath,
    '--feedback_type', params.feedback_type,
    '--message', params.message,
  ];

  if (params.skill_name) {
    args.push('--skill_name', params.skill_name);
  }

  if (params.conversation_context) {
    args.push('--conversation_context', params.conversation_context);
  }

  // Execute Python script
  return new Promise((resolve, reject) => {
    const python = spawn('python3', args);

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        const errorOutput = stderr || stdout;
        reject(new Error(`Failed to submit feedback: ${errorOutput}`));
        return;
      }

      // Parse output for SBO number
      const numberMatch = stdout.match(/successfully: (DSRT\d+)/);
      const linkMatch = stdout.match(/Link: (https:\/\/[^\s]+)/);

      const number = numberMatch ? numberMatch[1] : 'Unknown';
      const link = linkMatch ? linkMatch[1] : '';

      resolve({
        success: true,
        number: number,
        link: link,
        message: `Feedback submitted successfully: ${number}\n\n${link}`,
        raw_output: stdout,
      });
    });
  });
}

// Create MCP server instance
const server = new Server(
  {
    name: "saai-skill-feedback-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register tool handlers
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "submit_skill_feedback",
        description: `Submit feedback about any MCP skill you use with Claude.

Use this tool when the user:
- Reports a bug or issue with a skill
- Suggests an enhancement or improvement
- Requests a completely new skill

The tool will:
- Auto-detect which skill from recent conversation (if not specified)
- Capture relevant conversation context
- Create a ServiceNow SBO with all details
- Assign to the skill maintainer

Types of feedback:
- bug: Something is broken, errors, unexpected behavior
- enhancement: Improvements to existing features
- new_skill: Request for a new MCP skill that doesn't exist yet`,
        inputSchema: {
          type: "object",
          properties: {
            feedback_type: {
              type: "string",
              enum: ["bug", "enhancement", "new_skill"],
              description: "Type of feedback: bug (something broken), enhancement (improve existing), new_skill (request new capability)",
            },
            message: {
              type: "string",
              description: "Detailed feedback message with context from the conversation. For bugs: include error messages. For enhancements: describe current vs desired behavior. For new skills: explain the use case.",
            },
            skill_name: {
              type: "string",
              description: "Name of the skill (e.g., 'create-sbo-request'). Auto-detected from conversation if not provided.",
            },
            conversation_context: {
              type: "string",
              description: "Relevant conversation excerpt showing the issue (3-5 messages). Include tool calls, parameters, and responses if applicable.",
            },
          },
          required: ["feedback_type", "message"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "submit_skill_feedback") {
    try {
      const params = SubmitFeedbackSchema.parse(request.params.arguments);
      const result = await submitFeedback(params);

      return {
        content: [
          {
            type: "text",
            text: `✓ Thank you for your feedback!\n\n${result.message}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `✗ Error submitting feedback: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  } else {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("SAAI Skill Feedback MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
