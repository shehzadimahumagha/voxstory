"""
VoxStory — exporters/json_exporter.py

Converts VoxStory output to structured JSON compatible with Jira's REST API format.
This is the file that makes VoxStory feel like a real engineering tool.
"""

import json
import re
from typing import Any


def parse_stories_to_json(markdown_text: str, mode: str = "transcript") -> dict:
    """
    Parses VoxStory markdown output into a structured JSON object.
    Designed to be compatible with Jira issue import format.

    Args:
        markdown_text: The raw markdown string returned by the agent
        mode: "transcript" or "refinement"

    Returns:
        A dict with metadata and list of parsed stories
    """
    stories = []
    current_story: dict[str, Any] = {}
    current_section = None

    lines = markdown_text.split("\n")

    for line in lines:
        stripped = line.strip()

        # New story block
        if stripped.startswith("## Story"):
            if current_story:
                stories.append(current_story)
            title_match = re.match(r"## Story \d+:\s*(.+)", stripped)
            title = title_match.group(1).strip() if title_match else "Untitled Story"
            current_story = {
                "title": title,
                "user_story": "",
                "business_value": "",
                "priority": "",
                "acceptance_criteria": {"happy_path": [], "edge_cases": []},
                "non_functional_requirements": [],
                "open_questions": [],
                "stakeholders": [],
                "jira_format": {
                    "issuetype": {"name": "Story"},
                    "summary": title,
                    "description": "",
                    "priority": {"name": "Medium"},
                    "labels": ["voxstory-generated"],
                },
            }
            current_section = None
            continue

        if not current_story:
            continue

        # Detect section
        if stripped.startswith("**User Story:**"):
            current_section = "user_story"
            value = stripped.replace("**User Story:**", "").strip()
            if value:
                current_story["user_story"] = value
            continue

        if stripped.startswith("**Business Value:**"):
            current_section = "business_value"
            value = stripped.replace("**Business Value:**", "").strip()
            if value:
                current_story["business_value"] = value
            continue

        if stripped.startswith("**Priority:**"):
            current_section = "priority"
            priority_text = stripped.replace("**Priority:**", "").strip()
            # Extract just High/Medium/Low
            match = re.search(r"(High|Medium|Low)", priority_text, re.IGNORECASE)
            if match:
                priority = match.group(1).capitalize()
                current_story["priority"] = priority
                current_story["jira_format"]["priority"]["name"] = priority
            continue

        if stripped.startswith("**Acceptance Criteria:**"):
            current_section = "acceptance_criteria"
            continue

        if "*Happy Path:*" in stripped:
            current_section = "acceptance_criteria_happy"
            continue

        if "*Edge Cases" in stripped:
            current_section = "acceptance_criteria_edge"
            continue

        if stripped.startswith("**Non-Functional Requirements:**"):
            current_section = "nfr"
            continue

        if stripped.startswith("**Open Questions"):
            current_section = "open_questions"
            continue

        if stripped.startswith("**Stakeholders"):
            current_section = "stakeholders"
            continue

        if stripped == "---":
            current_section = None
            continue

        # Fill sections
        if current_section == "user_story" and stripped:
            if current_story["user_story"]:
                current_story["user_story"] += " " + stripped
            else:
                current_story["user_story"] = stripped

        elif current_section == "business_value" and stripped:
            if current_story["business_value"]:
                current_story["business_value"] += " " + stripped
            else:
                current_story["business_value"] = stripped

        elif current_section == "acceptance_criteria_happy" and stripped.startswith("- "):
            current_story["acceptance_criteria"]["happy_path"].append(stripped[2:])

        elif current_section == "acceptance_criteria_edge" and stripped.startswith("- "):
            current_story["acceptance_criteria"]["edge_cases"].append(stripped[2:])

        elif current_section == "nfr" and stripped.startswith("- "):
            current_story["non_functional_requirements"].append(stripped[2:])

        elif current_section == "open_questions" and stripped.startswith("- [ ]"):
            current_story["open_questions"].append(stripped[5:].strip())

        elif current_section == "stakeholders" and stripped.startswith("- "):
            current_story["stakeholders"].append(stripped[2:])

    # Capture last story
    if current_story:
        stories.append(current_story)

    # Build Jira description from user story + business value
    for story in stories:
        story["jira_format"]["summary"] = story["title"]
        story["jira_format"]["description"] = (
            f"*User Story:*\n{story['user_story']}\n\n"
            f"*Business Value:*\n{story['business_value']}"
        )

    return {
        "voxstory_version": "1.0",
        "mode": mode,
        "total_stories": len(stories),
        "stories": stories,
    }


def to_json_bytes(markdown_text: str, mode: str = "transcript") -> bytes:
    """
    Returns JSON-encoded bytes for Streamlit download.

    Args:
        markdown_text: VoxStory agent output
        mode: "transcript" or "refinement"

    Returns:
        UTF-8 encoded JSON bytes
    """
    data = parse_stories_to_json(markdown_text, mode)
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
