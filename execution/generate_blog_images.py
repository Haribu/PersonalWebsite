"""
generate_blog_images.py — Layer 3 Execution Script
====================================================
Generates a dark, cinematic header image for each draft post using
Google's Imagen 4 model via the google-genai SDK.

Input:  .tmp/draft_manifest.json  (slugs + draft paths)
        .tmp/drafts/<slug>.md     (reads frontmatter for title/summary)
Output: website/assets/header_<slug>.png

Exit codes:
  0 — Success (continues even if individual images fail — logged in manifest)
  1 — Fatal error (missing manifest or API key)
"""

import os
import sys
import json
import re
import base64

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXECUTION_DIR)
TMP_DIR = os.path.join(ROOT_DIR, ".tmp")
ASSETS_DIR = os.path.join(ROOT_DIR, "website", "assets")

MANIFEST_PATH = os.path.join(TMP_DIR, "draft_manifest.json")

IMAGE_MODEL = "imagen-4.0-generate-001"

# Base style prompt — keeps visual identity consistent across all posts
IMAGE_STYLE_SUFFIX = (
    "Dark cinematic abstract digital composition. "
    "Deep navy, dark teal, and slate colour palette with subtle electric blue highlights. "
    "Dramatic directional lighting. Ultra-detailed, photorealistic render. "
    "No text, no typography, no logos, no watermarks, no human faces. "
    "Wide landscape aspect ratio."
)

# Gemini Flash is used cheaply just to derive a safe image subject from the post metadata
SUBJECT_MODEL = "gemini-2.0-flash"


def extract_frontmatter(filepath: str) -> dict:
    """Extract title and summary from markdown frontmatter."""
    result = {"title": "", "summary": ""}
    if not os.path.exists(filepath):
        return result

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip().strip('"\'')

    summary_match = re.search(r'^summary:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if summary_match:
        result["summary"] = summary_match.group(1).strip().strip('"\'')

    return result


def derive_image_subject(client: genai.Client, title: str, summary: str) -> str:
    """
    Use Gemini Flash to derive a safe, specific image subject from post metadata.
    This avoids injecting raw post titles directly into the Imagen prompt.
    """
    prompt = (
        f"A blog post is titled: \"{title}\"\n"
        f"Summary: \"{summary}\"\n\n"
        "In 15 words or fewer, describe a specific abstract visual element that "
        "represents the theme of this post. The image will be dark and cinematic. "
        "Focus on abstract concepts: data flows, networks, shields, fractured code, "
        "surveillance nodes, digital landscapes. No people. No text. "
        "Return only the visual description, nothing else."
    )

    response = client.models.generate_content(
        model=SUBJECT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.4),
    )
    return response.text.strip()


def generate_image(client: genai.Client, subject: str, slug: str) -> str | None:
    """
    Generate a header image using Imagen 4. Returns the output filepath or None on failure.
    """
    full_prompt = f"{subject}. {IMAGE_STYLE_SUFFIX}"
    output_path = os.path.join(ASSETS_DIR, f"header_{slug}.png")

    print(f"  Prompt: {full_prompt[:120]}...")

    try:
        response = client.models.generate_images(
            model=IMAGE_MODEL,
            prompt=full_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
            ),
        )

        if not response.generated_images:
            print(f"  [WARN] Imagen returned no images for slug '{slug}'.")
            return None

        image_data = response.generated_images[0].image.image_bytes
        with open(output_path, "wb") as f:
            f.write(image_data)

        print(f"  ✓ Image saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"  [WARN] Image generation failed for '{slug}': {e}")
        return None


def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"[FATAL] {MANIFEST_PATH} not found. Run generate_blog_drafts.py first.", file=sys.stderr)
        sys.exit(1)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if not manifest:
        print("No drafts to generate images for.")
        sys.exit(0)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[FATAL] GOOGLE_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Generating images for {len(manifest)} post(s)...")
    print(f"{'='*60}\n")

    for entry in manifest:
        slug = entry["slug"]
        draft_path = entry["draft_path"]
        print(f"Post: {entry['suggested_title'][:60]}")

        frontmatter = extract_frontmatter(draft_path)
        title = frontmatter["title"] or entry["suggested_title"]
        summary = frontmatter["summary"] or ""

        # Derive a safe image subject
        subject = derive_image_subject(client, title, summary)
        print(f"  Subject derived: {subject}")

        image_path = generate_image(client, subject, slug)
        entry["image_path"] = image_path  # May be None if generation failed
        print()

    # Update manifest with image paths
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    succeeded = sum(1 for e in manifest if e.get("image_path"))
    print(f"✅ Generated {succeeded}/{len(manifest)} image(s).")


if __name__ == "__main__":
    main()
