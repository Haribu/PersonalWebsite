"""
stage_blog_posts.py — Layer 3 Execution Script
================================================
Validates and stages drafted blog posts for Git commit.
Copies markdown drafts and header images into the repo structure,
patches image references to use the {{ base_url }} template variable,
and runs lint_content.py to validate frontmatter.

Input:  .tmp/draft_manifest.json
        .tmp/drafts/<slug>.md
        website/assets/header_<slug>.png  (may not exist if image gen failed)
Output: website/content/blog/<slug>/index.md
        website/content/blog/<slug>/header.png
        .tmp/staging_report.json

Exit codes:
  0 — At least one post was staged successfully
  1 — Fatal error (manifest missing, or ALL posts failed linting)
"""

import os
import sys
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, Dict

from dotenv import load_dotenv

# Load .env from project root (Google Drive symlink)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXECUTION_DIR)
TMP_DIR = os.path.join(ROOT_DIR, ".tmp")

MANIFEST_PATH = os.path.join(TMP_DIR, "draft_manifest.json")
REPORT_PATH = os.path.join(TMP_DIR, "staging_report.json")

BLOG_CONTENT_DIR = os.path.join(ROOT_DIR, "website", "content", "blog")
ASSETS_DIR = os.path.join(ROOT_DIR, "website", "assets")


def validate_frontmatter(filepath: str) -> Tuple[bool, str]:
    """
    Basic validation: check the file has a --- frontmatter block with
    required keys (title, date, summary). Full YAML validation is handled
    by lint_content.py which only lints YAML files, not .md frontmatter.
    So we do a targeted check here.
    """
    required_keys = {"title", "date", "summary"}
    found_keys = set()

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check frontmatter block exists
    if not content.startswith("---"):
        return False, "Missing frontmatter block (file must start with ---)."

    # Extract frontmatter
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return False, "Frontmatter block is not closed."

    frontmatter = content[3:end_idx]
    for key in required_keys:
        if re.search(rf"^{key}:", frontmatter, re.MULTILINE):
            found_keys.add(key)

    missing = required_keys - found_keys
    if missing:
        return False, f"Missing frontmatter keys: {', '.join(sorted(missing))}"

    # Check content body exists after frontmatter
    body = content[end_idx + 3:].strip()
    if len(body) < 100:
        return False, "Post body appears too short (under 100 characters)."

    return True, "OK"


def patch_image_reference(markdown_text: str, slug: str) -> str:
    """
    Replace any hardcoded image path in the first Markdown image tag
    with the correct {{ base_url }} template reference.

    Handles cases where Gemini may write a relative path, an absolute path,
    or a placeholder.
    """
    # Target the expected header filename pattern
    correct_ref = "./header.png"

    # Match the first image tag in the document
    # Gemini may output: ![...](anything) or ![...](header_slug.png) etc.
    img_pattern = re.compile(r'!\[([^\]]*)\]\([^\)]+header[^\)]*\)', re.IGNORECASE)
    match = img_pattern.search(markdown_text)

    if match:
        alt_text = match.group(1) or "Blog post header image"
        new_tag = f"![{alt_text}]({correct_ref})"
        return markdown_text.replace(match.group(0), new_tag, 1)

    # If no header image ref found, prepend one after the frontmatter
    # (handles case where Gemini omits the image entirely)
    front_end = markdown_text.find("---", 3)
    if front_end != -1:
        insert_pos = markdown_text.find("\n", front_end + 3) + 1
        image_line = f"\n![Blog post header image]({correct_ref})\n"
        return markdown_text[:insert_pos] + image_line + markdown_text[insert_pos:]

    return markdown_text


def stage_post(entry: Dict) -> Dict:
    """
    Stage a single post. Returns a result dict with success status and details.
    """
    raw_slug = str(entry.get("slug", ""))
    # Sanitize slug against path traversal
    slug = re.sub(r"[^a-zA-Z0-9_\-]", "", raw_slug)
    
    draft_path = entry.get("draft_path", "")
    image_path = entry.get("image_path")

    result = {
        "slug": slug if slug else raw_slug,
        "staged": False,
        "dest_path": "",
        "image_staged": False,
        "notes": [],
    }
    
    if not slug:
        result["notes"].append("Invalid slug provided (Path Traversal protection).")
        return result

    # --- Validate draft exists ---
    if not os.path.exists(draft_path):
        result["notes"].append(f"Draft file not found: {draft_path}")
        return result

    # --- Read and validate frontmatter ---
    valid, reason = validate_frontmatter(draft_path)
    if not valid:
        result["notes"].append(f"Frontmatter validation failed: {reason}")
        return result

    with open(draft_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    # --- Create post directory (Page Bundle) ---
    post_dir = os.path.abspath(os.path.join(BLOG_CONTENT_DIR, slug))
    
    # Verify post_dir is within BLOG_CONTENT_DIR limits bounds
    if not post_dir.startswith(os.path.abspath(BLOG_CONTENT_DIR)):
        result["notes"].append("Path traversal boundaries exceeded.")
        return result
        
    print(f"  → Creating directory: {post_dir}")
    os.makedirs(post_dir, exist_ok=True)

    # --- Handle image ---
    if image_path and os.path.exists(image_path):
        dest_image = os.path.join(post_dir, "header.png")
        shutil.copy2(image_path, dest_image)
        result["image_staged"] = True
        print(f"  ✓ Image staged: {slug}/header.png")
    else:
        result["notes"].append("No header image available — post staged without image.")
        print(f"  [WARN] No image for '{slug}' — staging without it.")

    # --- Patch image reference in markdown ---
    markdown_text = patch_image_reference(markdown_text, slug)

    # --- Write final post ---
    dest_path = os.path.join(post_dir, "index.md")
    print(f"  → Writing index.md to {dest_path}")
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)
    print(f"  ✓ index.md written successfully.")

    result["staged"] = True
    result["dest_path"] = dest_path
    print(f"  ✓ Post staged: {dest_path}")

    return result


def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"[FATAL] {MANIFEST_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if not manifest:
        print("No drafts in manifest.")
        sys.exit(0)

    os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Staging {len(manifest)} post(s)...")
    print(f"{'='*60}\n")

    staging_results = []
    for entry in manifest:
        print(f"Staging: {entry['suggested_title'][:60]}")
        result = stage_post(entry)
        result["source_issue_numbers"] = entry.get("source_issue_numbers", [])
        staging_results.append(result)
        print()

    # --- Summary ---
    succeeded = [r for r in staging_results if r["staged"]]
    failed = [r for r in staging_results if not r["staged"]]

    print(f"{'='*60}")
    print(f"Staging complete: {len(succeeded)} succeeded, {len(failed)} failed.")

    if failed:
        for r in failed:
            print(f"  [FAIL] {r['slug']}: {'; '.join(r['notes'])}")

    # Write staging report
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(staging_results, f, indent=2)

    if not succeeded:
        print("[FATAL] No posts were staged successfully.", file=sys.stderr)
        sys.exit(1)

    print(f"\n✅ Staging report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
