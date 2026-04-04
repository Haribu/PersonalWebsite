"""
publish_blog_posts.py — Layer 3 Execution Script
================================================
Automates Step 7 & 8 of the blog generation workflow:
1. Creates a git branch for the batch
2. Commits staged files
3. Pushes to remote and creates a PR
4. Comments on, labels, and closes the source issues
"""

import os
import sys
import json
import subprocess
import re
import shutil
from datetime import datetime

EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXECUTION_DIR)
TMP_DIR = os.path.join(ROOT_DIR, ".tmp")
REPORT_PATH = os.path.join(TMP_DIR, "staging_report.json")
PR_BODY_PATH = os.path.join(TMP_DIR, "pr_body.md")

def run_cmd(cmd, check=True, capture=True):
    """Run a shell command and return its stdout."""
    print(f"  → Executing command: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=ROOT_DIR,
        capture_output=capture,
        text=True,
    )
    if check and result.returncode != 0:
        print(f"[FATAL] Command failed: {' '.join(cmd)}", file=sys.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout, file=sys.stderr)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    return result.stdout.strip() if capture else None

def parse_frontmatter_and_content(filepath):
    """Extracts title, calculates word count, and gets the first paragraph."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract title from frontmatter
    title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Untitled Post"

    # Separate body from frontmatter
    end_idx = content.find("---", 3)
    if end_idx != -1:
        body = content[end_idx + 3:].strip()
    else:
        body = content

    words = len(body.split())
    
    # First genuine paragraph (not an image, heading, or empty line)
    paragraphs = []
    for p in body.split("\n\n"):
        p = p.strip()
        if p and not p.startswith("!") and not p.startswith("#"):
            paragraphs.append(p)
            break
            
    preview = paragraphs[0] if paragraphs else "No preview available."
    # Truncate preview if it's too long
    if len(preview) > 300:
        preview = preview[:300] + "..."

    return title, words, preview

def cleanup_temporary_files():
    """Removes all files and subdirectories from the .tmp directory."""
    print(f"\n  → Cleaning up temporary files in {TMP_DIR}...")
    if not os.path.exists(TMP_DIR):
        print("  ✓ .tmp directory does not exist. Skipping.")
        return

    for item in os.listdir(TMP_DIR):
        item_path = os.path.join(TMP_DIR, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"  [WARN] Failed to delete {item_path}: {e}")

    print("  ✓ Temporary files cleaned up.")

def main():
    if not os.path.exists(REPORT_PATH):
        print(f"[FATAL] {REPORT_PATH} not found. Cannot publish.", file=sys.stderr)
        sys.exit(1)

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        staging_reports = json.load(f)

    staged_posts = [r for r in staging_reports if r.get("staged")]
    if not staged_posts:
        print("No successfully staged posts to publish.")
        sys.exit(0)

    date_str = datetime.now().strftime("%Y-%m-%d")
    branch_name = f"draft/weekly-batch-{date_str}"
    
    # Check if branch already exists locally; if so, append timestamp
    existing_branches = run_cmd(["git", "branch", "--list", branch_name])
    if existing_branches:
        branch_name += f"-{int(datetime.now().timestamp())}"

    # 1. Git branch, add, commit, push
    run_cmd(["git", "checkout", "-b", branch_name])
    run_cmd(["git", "add", "website/content/blog/"])
    
    # Check if there is anything to commit
    status = run_cmd(["git", "status", "--porcelain"])
    if not status:
        print("No changes to commit. Exiting.")
        run_cmd(["git", "checkout", "main"], check=False)
        sys.exit(0)
        
    run_cmd(["git", "commit", "-m", f"draft: weekly blog batch {date_str}"])
    run_cmd(["git", "push", "-u", "origin", branch_name])

    # 2. Build PR Body
    pr_body_lines = [
        f"Weekly Blog Batch ({date_str})",
        "",
        f"Processed {len(staged_posts)} article(s) from the reading queue into published posts.",
        ""
    ]

    all_issue_numbers = set()

    for idx, post in enumerate(staged_posts, 1):
        if str(post.get('slug')) == "untitled":
             continue

        title, words, preview = parse_frontmatter_and_content(post["dest_path"])
        issues = post.get("source_issue_numbers", [])
        
        for issue in issues:
            all_issue_numbers.add(issue)

        pr_body_lines.append(f"## {idx}. {title}")
        pr_body_lines.append("")
        pr_body_lines.append(f"Word Count: ~{words} words")
        if issues:
            pr_body_lines.append(f"Source Issue(s): {', '.join([f'#{i}' for i in issues])}")
        pr_body_lines.append("")
        pr_body_lines.append("### Draft Preview")
        pr_body_lines.append("")
        
        # Quote block the preview
        for line in preview.split("\n"):
            pr_body_lines.append(f"> {line}")
        pr_body_lines.append("")

    print(f"  → Generating PR body markdown...")
    with open(PR_BODY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(pr_body_lines))
    print(f"  ✓ PR body written to {PR_BODY_PATH}")

    # 3. Create PR
    pr_title = f"[Blog Draft] Week of {date_str} — {len(staged_posts)} post(s)"
    pr_url = run_cmd([
        "gh", "pr", "create",
        "--title", pr_title,
        "--body-file", PR_BODY_PATH,
        "--base", "main",
        "--assignee", "@me"
    ])
    
    print(f"\n✅ PR Created: {pr_url}")

    # 4. Update source issues
    for issue_num in all_issue_numbers:
        print(f"Updating Issue #{issue_num}...")
        # Comment
        run_cmd([
            "gh", "issue", "comment", str(issue_num),
            "--body", f"✅ Processed — see PR: {pr_url}"
        ])
        # Edit labels
        run_cmd([
            "gh", "issue", "edit", str(issue_num),
            "--remove-label", "blog-queue",
            "--add-label", "blog-processed"
        ])
        # Close issue
        run_cmd([
            "gh", "issue", "close", str(issue_num)
        ])
        print(f"  ✓ Issue #{issue_num} closed.")

    print("\n🎉 Publish pipeline complete.")

    # 5. Clean up temporary files
    cleanup_temporary_files()

    # Return to main branch
    run_cmd(["git", "checkout", "main"], check=False)

if __name__ == "__main__":
    main()
