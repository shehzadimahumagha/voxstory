"""
VoxStory — tests/test_exporters.py

Unit tests for docx and json exporters.
No API calls needed — tests pure transformation logic.
"""

import json
import pytest
from exporters.docx_exporter import markdown_to_docx
from exporters.json_exporter import parse_stories_to_json, to_json_bytes


# ── Fixtures ──────────────────────────────────────────────────────────────────

SAMPLE_MARKDOWN = """
## Story 1: Password Reset via Email

**User Story:**
As a registered customer, I want to reset my password via email, so that I can regain access to my account.

**Business Value:**
Reduces support calls and improves customer self-service.

**Priority:** High
*Rationale: Directly impacts user access and retention*

**Acceptance Criteria:**

*Happy Path:*
- Given I am on the login page
  When I click "Forgot Password" and enter my email
  Then I receive a one-time reset link valid for 24 hours

*Edge Cases & Error Scenarios:*
- Given I enter an unregistered email
  When I submit the form
  Then I see a generic message that does not reveal account existence

**Non-Functional Requirements:**
- Security: Reset links must be single-use

**Open Questions & Assumptions:**
- [ ] What is the exact wording of the confirmation email?

**Stakeholders & Roles:**
- Product Owner: Approves requirements

---
"""


# ── Tests: DOCX Exporter ──────────────────────────────────────────────────────

class TestDocxExporter:

    def test_returns_bytes(self):
        result = markdown_to_docx(SAMPLE_MARKDOWN, mode="Transcript")
        assert isinstance(result, bytes)

    def test_output_is_non_empty(self):
        result = markdown_to_docx(SAMPLE_MARKDOWN, mode="Transcript")
        assert len(result) > 0

    def test_works_with_refinement_mode(self):
        result = markdown_to_docx(SAMPLE_MARKDOWN, mode="Refinement")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_handles_empty_input(self):
        result = markdown_to_docx("", mode="Transcript")
        assert isinstance(result, bytes)

    def test_handles_plain_text(self):
        result = markdown_to_docx("Just a plain sentence with no markdown.", mode="Transcript")
        assert isinstance(result, bytes)
        assert len(result) > 0


# ── Tests: JSON Exporter ──────────────────────────────────────────────────────

class TestJsonExporter:

    def test_returns_dict(self):
        result = parse_stories_to_json(SAMPLE_MARKDOWN, mode="transcript")
        assert isinstance(result, dict)

    def test_has_required_top_level_keys(self):
        result = parse_stories_to_json(SAMPLE_MARKDOWN, mode="transcript")
        assert "voxstory_version" in result
        assert "mode" in result
        assert "total_stories" in result
        assert "stories" in result

    def test_detects_one_story(self):
        result = parse_stories_to_json(SAMPLE_MARKDOWN, mode="transcript")
        assert result["total_stories"] == 1

    def test_story_has_title(self):
        result = parse_stories_to_json(SAMPLE_MARKDOWN, mode="transcript")
        story = result["stories"][0]
        assert story["title"] == "Password Reset via Email"

    def test_story_has_priority(self):
        result = parse_stories_to_json(SAMPLE_MARKDOWN, mode="transcript")
        story = result["stories"][0]
        assert story["priority"] == "High"

    def test_story_has_open_questions(self):
        result = parse_stories_to_json(SAMPLE_MARKDOWN, mode="transcript")
        story = result["stories"][0]
        assert len(story["open_questions"]) > 0

    def test_jira_format_present(self):
        result = parse_stories_to_json(SAMPLE_MARKDOWN, mode="transcript")
        story = result["stories"][0]
        assert "jira_format" in story
        assert story["jira_format"]["issuetype"]["name"] == "Story"
        assert "voxstory-generated" in story["jira_format"]["labels"]

    def test_to_json_bytes_returns_valid_json(self):
        result = to_json_bytes(SAMPLE_MARKDOWN, mode="transcript")
        assert isinstance(result, bytes)
        parsed = json.loads(result.decode("utf-8"))
        assert "stories" in parsed

    def test_handles_empty_input(self):
        result = parse_stories_to_json("", mode="transcript")
        assert result["total_stories"] == 0
        assert result["stories"] == []
