"""
write_draft.py — Layer 3 Execution Script
==========================================
Writes blog post drafts to the .tmp/drafts/ folder with granular logging.
Usage: python execution/write_draft.py <slug>
Content is passed via stdin.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# Config
EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXECUTION_DIR)
DRAFTS_DIR = os.path.join(ROOT_DIR, ".tmp", "drafts")

def main():
    parser = argparse.ArgumentParser(description="Write a blog post draft with logging.")
    parser.add_argument("slug", help="Slug for the post filename.")
    args = parser.parse_args()

    # Create/Clean drafts directory
    print(f"  → Preparing drafts directory: {DRAFTS_DIR}")
    if os.path.exists(DRAFTS_DIR):
        print(f"  → Emptying existing drafts directory...")
        for item in os.listdir(DRAFTS_DIR):
            item_path = os.path.join(DRAFTS_DIR, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.unlink(item_path)
            except Exception as e:
                print(f"  [WARN] Failed to delete {item_path}: {e}")
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    print(f"  ✓ Drafts directory ready.")

    # Read content from stdin
    print(f"  → Reading blog post content from stdin...")
    try:
        content = sys.stdin.read()
        if not content:
            print(f"  [FATAL] No content provided in stdin.")
            sys.exit(1)
        print(f"  ✓ Read {len(content)} characters of content.")
    except Exception as e:
        print(f"  [FATAL] Failed to read from stdin: {e}")
        sys.exit(1)

    # Write file
    filepath = os.path.join(DRAFTS_DIR, f"{args.slug}.md")
    print(f"  → Writing draft to {filepath}...")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ Successfully wrote {args.slug}.md")
    except Exception as e:
        print(f"  [FATAL] Failed to write file: {e}")
        sys.exit(1)

    print(f"\n🎉 Drafting complete for slug: {args.slug}\n")

if __name__ == "__main__":
    main()
