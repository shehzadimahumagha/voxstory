"""
VoxStory — agent/github_tools.py

GitHub integration: validate repos, browse file trees, read file contents,
and fetch issues to inject as context into agent prompts.

Requires GITHUB_TOKEN in .env (fine-grained token with Contents + Issues read access).
"""

import os
from typing import Optional

from github import Github, GithubException, UnknownObjectException


def get_github_client() -> Github:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not found. Add GITHUB_TOKEN=your_token to your .env file."
        )
    return Github(token)


def validate_and_connect(repo_path: str) -> dict:
    """
    Validates access to a GitHub repo and returns basic metadata.
    repo_path: 'owner/repo'
    """
    try:
        g = get_github_client()
        repo = g.get_repo(repo_path)
        topics: list = []
        try:
            topics = repo.get_topics()
        except Exception:
            pass
        return {
            "valid": True,
            "name": repo.full_name,
            "description": repo.description or "",
            "language": repo.language or "Unknown",
            "stars": repo.stargazers_count,
            "topics": topics,
            "default_branch": repo.default_branch,
            "private": repo.private,
        }
    except UnknownObjectException:
        return {"valid": False, "error": "Repository not found or access denied."}
    except ValueError as e:
        return {"valid": False, "error": str(e)}
    except Exception as e:
        return {"valid": False, "error": f"Connection failed: {e}"}


def get_repo_tree(repo_path: str, max_items: int = 200) -> list[dict]:
    """
    Returns a flat list of all files and dirs (breadth-first traversal).
    Each item: { path, type, size }
    """
    g = get_github_client()
    repo = g.get_repo(repo_path)
    items: list[dict] = []
    try:
        stack = list(repo.get_contents(""))
        while stack and len(items) < max_items:
            item = stack.pop(0)
            items.append(
                {
                    "path": item.path,
                    "type": item.type,
                    "size": item.size if item.type == "file" else 0,
                }
            )
            if item.type == "dir":
                try:
                    children = list(repo.get_contents(item.path))
                    stack = children + stack
                except Exception:
                    pass
    except Exception as e:
        raise RuntimeError(f"Could not fetch repo tree: {e}")
    return items


def get_file_content(repo_path: str, file_path: str, max_chars: int = 6000) -> str:
    """Returns the decoded text content of a file, truncated to max_chars."""
    g = get_github_client()
    repo = g.get_repo(repo_path)
    try:
        content = repo.get_contents(file_path)
        if content.encoding == "base64":
            text = content.decoded_content.decode("utf-8", errors="replace")
            if len(text) > max_chars:
                text = text[:max_chars] + f"\n\n... [truncated at {max_chars} chars]"
            return text
        return "[Binary file — cannot display]"
    except Exception as e:
        raise RuntimeError(f"Could not read '{file_path}': {e}")


def get_repo_issues(
    repo_path: str, state: str = "open", limit: int = 15
) -> list[dict]:
    """Returns recent issues (PRs excluded)."""
    g = get_github_client()
    repo = g.get_repo(repo_path)
    result: list[dict] = []
    try:
        for issue in repo.get_issues(state=state):
            if len(result) >= limit:
                break
            if issue.pull_request:
                continue
            result.append(
                {
                    "number": issue.number,
                    "title": issue.title,
                    "body": (issue.body or "")[:400],
                    "labels": [lb.name for lb in issue.labels],
                    "state": issue.state,
                    "url": issue.html_url,
                }
            )
    except Exception as e:
        raise RuntimeError(f"Could not fetch issues: {e}")
    return result


def build_context_block(
    repo_info: dict,
    files: list[tuple[str, str]],
    issues: list[dict],
) -> str:
    """
    Formats GitHub repo data into a structured context block
    suitable for injection into a prompt.

    files: list of (path, content) tuples
    """
    parts = ["## GitHub Repository Context\n"]
    parts.append(f"**Repository:** {repo_info['name']}")
    if repo_info.get("description"):
        parts.append(f"**Description:** {repo_info['description']}")
    if repo_info.get("language"):
        parts.append(f"**Primary Language:** {repo_info['language']}")
    if repo_info.get("topics"):
        parts.append(f"**Topics:** {', '.join(repo_info['topics'])}")

    if files:
        parts.append("\n### Selected Code Files:")
        for path, content in files:
            ext = path.rsplit(".", 1)[-1] if "." in path else ""
            parts.append(f"\n**`{path}`**")
            parts.append(f"```{ext}\n{content}\n```")

    if issues:
        parts.append("\n### Open Issues:")
        for issue in issues:
            labels = (
                f" [{', '.join(issue['labels'])}]" if issue["labels"] else ""
            )
            parts.append(f"- #{issue['number']}: **{issue['title']}**{labels}")
            if issue.get("body"):
                parts.append(f"  {issue['body'][:200]}")

    return "\n".join(parts)
