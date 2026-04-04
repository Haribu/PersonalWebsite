"""
fetch_queue.py — Layer 3 Execution Script
==========================================
Fetches all open GitHub Issues labelled 'blog-queue' from the PersonalWebsite
repo that were created within the past 8 days. Parses Harry's article URL,
Feedly content, highlight, note, and any manual comments from each issue.

Input:  GitHub API (env: GH_PAT or GITHUB_TOKEN)
Output: .tmp/queue.json

Exit codes:
  0 — Success (queue.json written, may be empty list)
  1 — Fatal error (API failure, missing credentials)
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta, timezone

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO = "Haribu/PersonalWebsite"
LABEL = "blog-queue"
LOOKBACK_DAYS = 8  # Covers issues saved over the weekend before Monday batch

EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXECUTION_DIR)
TMP_DIR = os.path.join(ROOT_DIR, ".tmp")
OUTPUT_PATH = os.path.join(TMP_DIR, "queue.json")


def get_token() -> str:
    """Resolve GitHub token — prefers GH_PAT, falls back to GITHUB_TOKEN."""
    token = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
    if not token:
        print("[FATAL] No GitHub token found. Set GH_PAT or GITHUB_TOKEN.", file=sys.stderr)
        sys.exit(1)
    return token


def github_get(url: str, token: str, params: dict = None) -> dict | list:
    """Make an authenticated GitHub API GET request."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url, headers=headers, params=params, timeout=30)
    if response.status_code == 401:
        print("[FATAL] GitHub token is invalid or expired.", file=sys.stderr)
        sys.exit(1)
    response.raise_for_status()
    return response.json()


def parse_issue_body(body: str) -> dict:
    """
    Extract structured fields from the Zapier-generated issue body.

    Expected format (from Zapier template):
      ## Article Metadata
      - **URL:** <url>
      - **Source:** <source>
      - **Author:** <author>
      - **Date:** <date>

      ## Article Content (from Feedly)
      <content>

      ## Harry's Annotations
      **Highlight:** <highlight>
      **Note:** <note>
    """
    result = {
        "url": "",
        "source": "",
        "author": "",
        "published": "",
        "feedly_content": "",
        "highlight": "",
        "note": "",
    }

    if not body:
        return result

    # Extract URL
    url_match = re.search(r"\*\*URL:\*\*\s*(.+)", body)
    if url_match:
        result["url"] = url_match.group(1).strip()

    # Extract Source
    source_match = re.search(r"\*\*Source:\*\*\s*(.+)", body)
    if source_match:
        result["source"] = source_match.group(1).strip()

    # Extract Author
    author_match = re.search(r"\*\*Author:\*\*\s*(.+)", body)
    if author_match:
        result["author"] = author_match.group(1).strip()

    # Extract Published date
    date_match = re.search(r"\*\*Date:\*\*\s*(.+)", body)
    if date_match:
        result["published"] = date_match.group(1).strip()

    # Extract Article Content (between the two ## headers)
    content_match = re.search(
        r"## Article Content \(from Feedly\)\n(.*?)(?=\n## Harry's Annotations|\Z)",
        body,
        re.DOTALL,
    )
    if content_match:
        result["feedly_content"] = content_match.group(1).strip()

    # Extract Highlight
    highlight_match = re.search(r"\*\*Highlight:\*\*\s*(.+)", body)
    if highlight_match:
        result["highlight"] = highlight_match.group(1).strip()

    # Extract Note
    note_match = re.search(r"\*\*Note:\*\*\s*(.+)", body)
    if note_match:
        result["note"] = note_match.group(1).strip()

    return result


def fetch_issue_comments(issue_number: int, token: str) -> list[str]:
    """Fetch all human comments on an issue (excludes bot comments)."""
    url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}/comments"
    comments_data = github_get(url, token)
    comments = []
    for c in comments_data:
        # Skip bot/automated comments
        if c.get("user", {}).get("type") == "Bot":
            continue
        body = c.get("body", "").strip()
        if body:
            comments.append(body)
    return comments


def fetch_queue() -> list[dict]:
    """Fetch and parse all blog-queue issues from the past LOOKBACK_DAYS days."""
    token = get_token()
    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

    print(f"Fetching issues labelled '{LABEL}' from the past {LOOKBACK_DAYS} days...")

    url = f"https://api.github.com/repos/{REPO}/issues"
    params = {
        "labels": LABEL,
        "state": "open",
        "per_page": 100,
        "sort": "created",
        "direction": "asc",
    }

    all_issues = github_get(url, token, params)

    queued_articles = []
    for issue in all_issues:
        created_at_str = issue.get("created_at", "")
        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))

        if created_at < cutoff:
            print(f"  Skipping issue #{issue['number']} — older than {LOOKBACK_DAYS} days.")
            continue

        issue_number = issue["number"]
        title = issue.get("title", "").removeprefix("[Queue] ").strip()
        body = issue.get("body", "")

        parsed = parse_issue_body(body)
        comments = fetch_issue_comments(issue_number, token)

        article = {
            "issue_number": issue_number,
            "issue_title": title,
            "url": parsed["url"],
            "source": parsed["source"],
            "author": parsed["author"],
            "published": parsed["published"],
            "feedly_content": parsed["feedly_content"],
            "highlight": parsed["highlight"],
            "note": parsed["note"],
            "additional_comments": comments,
        }

        queued_articles.append(article)
        print(f"  ✓ Issue #{issue_number}: {title[:60]}")

    return queued_articles


def main():
    os.makedirs(TMP_DIR, exist_ok=True)

    queue = fetch_queue()

    if not queue:
        print("No articles queued this week. Exiting cleanly.")
        # Write empty queue so downstream scripts can check
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
        sys.exit(0)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Queued {len(queue)} article(s). Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
