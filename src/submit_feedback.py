#!/usr/bin/env python3
"""
Submit Feedback for MCP Skills

Creates feedback SBOs in ServiceNow with conversation context.
Works with ANY MCP skill - auto-detects which skill from conversation.

Usage:
    python3 submit_feedback.py --feedback_type bug --message "Dashboard lookup failed" --skill_name create-sbo-request
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Try to import session manager (if available)
try:
    from utils.session_manager import ServiceNowSession, AuthenticationError
    HAS_SESSION_MANAGER = True
except ImportError:
    HAS_SESSION_MANAGER = False
    print("Warning: session_manager not found - authentication may fail", file=sys.stderr)

# ServiceNow instance configuration
INSTANCE = "https://surf.service-now.com"
TABLE = "x_snc_security_d_0_dsrtable"

# Feedback type emoji mapping
EMOJI_MAP = {
    'bug': '🐛',
    'enhancement': '✨',
    'new_skill': '💡',
}


def build_description(feedback_type, message, skill_name, conversation_context):
    """Build comprehensive feedback description."""
    parts = []

    # Feedback header
    emoji = EMOJI_MAP.get(feedback_type, '📋')
    type_label = feedback_type.replace('_', ' ').title()
    parts.append(f"**{emoji} {type_label}**\n")

    # User message
    parts.append(f"**User Message:**\n{message}\n")

    # Skill name
    if skill_name:
        parts.append(f"\n**Affected Skill:** {skill_name}")

    # Add conversation context if available
    if conversation_context:
        parts.append("\n**Conversation Context:**")
        parts.append(conversation_context)

    # Signature
    parts.append("\n---")
    parts.append("*Submitted via saai-skill-feedback*")

    return '\n'.join(parts)


def create_feedback_sbo(feedback_type, message, skill_name=None, conversation_context=None):
    """Create a feedback SBO in ServiceNow."""

    # Build description
    description = build_description(feedback_type, message, skill_name, conversation_context)

    # Build title
    emoji = EMOJI_MAP.get(feedback_type, '📋')
    type_label = feedback_type.replace('_', ' ').title()

    if feedback_type == 'new_skill':
        title = f"{emoji} New Skill Request"
    else:
        skill_display = skill_name if skill_name else 'MCP Skill'
        title = f"{emoji} {type_label}: {skill_display}"

    # Prepare payload
    payload = {
        "short_description": title,
        "description": description,
        "data_science_request": "NOW Platform App Development",
        "work_activity": "Platform Dev - Security BOS App",
        "work_required_hrs": "4",  # Default estimate
        "state": "opened",
        "assigned_to": "David Rider",  # Skill maintainer
    }

    # Create the SBO
    url = f"{INSTANCE}/api/now/table/{TABLE}"

    print(f"\nSubmitting feedback: {title}")

    # Use session manager if available
    if HAS_SESSION_MANAGER:
        try:
            session = ServiceNowSession()
            response = session.post(url, json=payload)
        except AuthenticationError as e:
            print(f"\n❌ Authentication error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)
    else:
        # Fallback to basic auth (not recommended)
        import requests
        token = os.environ.get('SNOW_TOKEN')
        user = os.environ.get('SNOW_USER')
        password = os.environ.get('SNOW_PASS')

        if token:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            response = requests.post(url, headers=headers, json=payload)
        elif user and password:
            response = requests.post(url, auth=(user, password), json=payload)
        else:
            print(f"\n❌ No authentication credentials found")
            print(f"  Set SNOW_TOKEN or SNOW_USER/SNOW_PASS environment variables")
            sys.exit(1)

    # Handle response
    if response.status_code == 201:
        result = response.json().get("result", {})
        number = result.get("number", "Unknown")
        sys_id = result.get("sys_id", "")

        # Build link with datascience view
        link = f"{INSTANCE}/now/nav/ui/classic/params/target/{TABLE}.do%3Fsys_id%3D{sys_id}%26sysparm_view%3Ddatascience%26sysparm_record_target%3D{TABLE}%26sysparm_record_row%3D1%26sysparm_record_rows%3D1881%26sysparm_record_list%3Drequest_type%253DSecurity%2BData%2BAnalytics%255EORDERBYDESCnumber%26sysparm_view%3Ddatascience"

        print(f"✓ Feedback submitted successfully: {number}")
        print(f"\nLink: {link}")

        return {
            'number': number,
            'sys_id': sys_id,
            'link': link
        }
    else:
        print(f"\n✗ Failed to submit feedback")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Submit feedback about MCP skills")
    parser.add_argument(
        "--feedback_type",
        required=True,
        choices=['bug', 'enhancement', 'new_skill'],
        help="Type of feedback"
    )
    parser.add_argument(
        "--message",
        required=True,
        help="Feedback message"
    )
    parser.add_argument(
        "--skill_name",
        help="Name of the skill being reported (auto-detected if not provided)"
    )
    parser.add_argument(
        "--conversation_context",
        help="Relevant conversation excerpt showing the issue"
    )

    args = parser.parse_args()

    create_feedback_sbo(
        feedback_type=args.feedback_type,
        message=args.message,
        skill_name=args.skill_name,
        conversation_context=args.conversation_context
    )


if __name__ == "__main__":
    main()
