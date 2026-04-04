"""
generate_blog_drafts.py — Layer 3 Execution Script
====================================================
Two-stage Gemini pipeline:
  Stage 1 — Collective analysis: given all articles + Harry's annotations,
             decide how many posts to write and define the structure of each.
  Stage 2 — Writing: for each decided post, generate a full ~750-word blog
             post in Harry McLaren's established authorial voice.

Input:  .tmp/articles.json
Output: .tmp/drafts/<slug>.md (1 or more files)
        .tmp/draft_manifest.json (metadata for downstream scripts)

Exit codes:
  0 — Success
  1 — Fatal error
"""

import os
import sys
import json
import re
from datetime import date, datetime

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXECUTION_DIR)
TMP_DIR = os.path.join(ROOT_DIR, ".tmp")
DRAFTS_DIR = os.path.join(TMP_DIR, "drafts")
BLOG_CONTENT_DIR = os.path.join(ROOT_DIR, "website", "content", "blog")

INPUT_PATH = os.path.join(TMP_DIR, "articles.json")
MANIFEST_PATH = os.path.join(TMP_DIR, "draft_manifest.json")

# Cap posts per batch (see SOP edge cases)
MAX_POSTS_PER_BATCH = 3

ANALYSIS_MODEL = "gemini-2.5-pro"
WRITING_MODEL = "gemini-2.5-pro"

# ---------------------------------------------------------------------------
# Authorial Voice Brief (mirrors .agents/workflows/generate_blog_post.md)
# ---------------------------------------------------------------------------
VOICE_BRIEF = """
You are Harry McLaren, Head of Cyber Defence. You write for your personal blog
"Transmission Log" at harrymclaren.co.uk.

YOUR INTELLECTUAL TERRITORY: The "Collision Space" — the intersection of emerging
AI capability and established security frameworks (NIST CSF, ISO 27001, NIST AI RMF).
You are not an academic. You are a practitioner with operational experience.

YOUR TONE:
- Direct and analytical. Assertive, not arrogant.
- Conversational but precise — as if briefing a senior peer, not writing a paper.
- You name phenomena. You coin terms (e.g. "Context Rot", "Synthetic Authority",
  "Epistemic Capture"). Named phenomena make ideas portable and memorable.
- Comfortable challenging consensus. You include adversarial critique perspectives.
- Never breathless or hyperbolic. Never use: "in conclusion", "it is important to note",
  "game-changer", "paradigm shift", "unprecedented".

YOUR STRUCTURE (every post):
1. Hook paragraph — a sharp observation or reframe. Do NOT simply restate the title.
2. Named phenomenon — introduce or invoke a specific term for the problem.
3. 2–4 ### subheadings — each covering a distinct analytical angle.
4. Adversarial / Critical section — steelman the counterargument or failure mode.
   Title this section "The Red Team Perspective" or "Critical Review".
5. Concrete recommendations — a numbered list, actionable and specific.
   Not generic advice. Real operational guidance.

YOUR STYLE RULES:
- **Bold** key terms on first use.
- *Italics* sparingly for emphasis only.
- Cite sources inline as hyperlinks: "...as argued in [this analysis](URL)..."
- Include "Recommended Reading" section at the end only if 2+ sources genuinely merit it.
- Avoid passive voice. Avoid hedging ("it could be argued", "one might say").
- Target length: 700–900 words. Do not pad. Quality over length.

FRONTMATTER: Every post must begin with valid YAML frontmatter:
---
title: "Post Title Here"
date: "YYYY-MM-DD"
summary: "A single punchy sentence. Under 160 characters."
---

The date must be today: {today}
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert a title to a safe filename slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    text = text.strip("_")
    return text[:50]


def unique_slug(base_slug: str) -> str:
    """Ensure slug doesn't collide with existing blog posts."""
    existing = set()
    if os.path.exists(BLOG_CONTENT_DIR):
        for f in os.listdir(BLOG_CONTENT_DIR):
            existing.add(os.path.splitext(f)[0])

    slug = base_slug
    counter = 2
    while slug in existing:
        slug = f"{base_slug}_{counter}"
        counter += 1
    return slug


def format_article_for_prompt(article: dict) -> str:
    """Format a single article entry for inclusion in a Gemini prompt."""
    parts = [
        f"### Article: {article.get('issue_title', 'Untitled')}",
        f"**Source URL:** {article.get('url', 'N/A')}",
        f"**Published by:** {article.get('source', 'Unknown')}",
        "",
        "**Article Text:**",
        article.get("full_text", "")[:4000],  # Trim to avoid token overrun
    ]

    highlight = article.get("highlight", "").strip()
    note = article.get("note", "").strip()
    comments = article.get("additional_comments", [])

    if highlight and highlight not in ("None", ""):
        parts.append(f"\n**Harry's Highlight (key passage he found significant):**\n> {highlight}")
    if note and note not in ("None", ""):
        parts.append(f"\n**Harry's Note (his initial reaction):**\n{note}")
    if comments:
        parts.append("\n**Harry's Additional Thoughts (from issue comments):**")
        for c in comments:
            parts.append(f"- {c}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Stage 1: Collective Analysis
# ---------------------------------------------------------------------------

ANALYSIS_SYSTEM = """You are an editorial analyst for Harry McLaren's blog "Transmission Log".
Harry is Head of Cyber Defence. His territory is the "Collision Space" between AI and security frameworks.

Given a batch of articles Harry has been reading (with his annotations), your job is to:
1. Identify the thematic structure of this week's reading.
2. Decide how many blog posts should be written (1 to {max_posts}).
3. For each post, define its structure precisely.

RULES:
- If multiple articles share a strong thematic thread, combine them into one synthesised post.
- If articles cover genuinely distinct topics, recommend separate posts.
- Harry's highlights and notes are directional signals — use them to identify what he wants to emphasise.
- Prefer depth over breadth. One excellent post beats three thin ones.
- Maximum {max_posts} posts regardless of how many articles are queued.

OUTPUT: Respond ONLY with valid JSON in this exact schema, no markdown, no preamble:
{{
  "posts": [
    {{
      "suggested_title": "string",
      "central_argument": "string (1–2 sentences)",
      "harry_angle": "string — Harry's perspective/reaction, derived from his annotations",
      "source_issue_numbers": [list of integers],
      "recommended_sections": ["Section 1 title", "Section 2 title", "..."],
      "named_phenomenon": "string — a term to coin or invoke for this post's central idea"
    }}
  ]
}}
""".format(max_posts=MAX_POSTS_PER_BATCH)


def run_analysis(client: genai.Client, articles: list[dict]) -> list[dict]:
    """Stage 1: collective analysis to decide post count and structure."""
    articles_text = "\n\n---\n\n".join(format_article_for_prompt(a) for a in articles)

    user_prompt = f"""Here are the articles Harry read this week:\n\n{articles_text}

Based on these articles and Harry's annotations, decide how many posts to write and define each one.
Return valid JSON only."""

    print("  Running Stage 1: Collective analysis...")
    response = client.models.generate_content(
        model=ANALYSIS_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=ANALYSIS_SYSTEM,
            temperature=0.3,  # Low temp for structured JSON output
        ),
        contents=user_prompt,
    )

    raw = response.text.strip()
    # Strip markdown code fences if Gemini wraps in them
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    try:
        result = json.loads(raw)
        posts = result.get("posts", [])
        if not posts:
            raise ValueError("Empty posts array in analysis response.")
        return posts[:MAX_POSTS_PER_BATCH]
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[FATAL] Analysis response was not valid JSON: {e}", file=sys.stderr)
        print(f"Raw response:\n{raw}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Stage 2: Writing
# ---------------------------------------------------------------------------

def build_writing_prompt(post_plan: dict, relevant_articles: list[dict]) -> str:
    """Construct the writing prompt for a single post."""
    articles_text = "\n\n---\n\n".join(format_article_for_prompt(a) for a in relevant_articles)

    return f"""Write a blog post for Harry McLaren's "Transmission Log" based on the following brief:

## Post Brief
**Suggested Title:** {post_plan['suggested_title']}
**Central Argument:** {post_plan['central_argument']}
**Harry's Angle:** {post_plan['harry_angle']}
**Named Phenomenon to use:** {post_plan.get('named_phenomenon', '[coin an appropriate term]')}
**Recommended Structure:**
{chr(10).join(f"- {s}" for s in post_plan.get('recommended_sections', []))}

## Source Material
{articles_text}

---
Write the complete blog post now. Start with the YAML frontmatter block, then the content.
Do not include any preamble, explanation, or commentary outside the post itself.
"""


def run_writing_pass(
    client: genai.Client,
    post_plan: dict,
    relevant_articles: list[dict],
    today: str,
) -> str:
    """Stage 2: generate the full post for a single post plan."""
    system = VOICE_BRIEF.format(today=today)
    user_prompt = build_writing_prompt(post_plan, relevant_articles)

    print(f"  Writing post: \"{post_plan['suggested_title'][:60]}\"...")
    response = client.models.generate_content(
        model=WRITING_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.75,  # More creative for prose
        ),
        contents=user_prompt,
    )
    return response.text.strip()


# ---------------------------------------------------------------------------
# Frontmatter extraction
# ---------------------------------------------------------------------------

def extract_frontmatter_title(markdown_text: str) -> str:
    """Pull the title from YAML frontmatter for slug generation."""
    match = re.search(r'^---\s*\ntitle:\s*["\']?(.+?)["\']?\s*\n', markdown_text, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"\'')
    return "untitled_post"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not os.path.exists(INPUT_PATH):
        print(f"[FATAL] {INPUT_PATH} not found. Run scrape_article.py first.", file=sys.stderr)
        sys.exit(1)

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        articles = json.load(f)

    if not articles:
        print("No articles to process.")
        with open(MANIFEST_PATH, "w") as f:
            json.dump([], f)
        sys.exit(0)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[FATAL] GOOGLE_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    today = date.today().isoformat()
    os.makedirs(DRAFTS_DIR, exist_ok=True)

    # Map issue numbers to article dicts for easy lookup
    articles_by_issue = {a["issue_number"]: a for a in articles}

    # --- Stage 1: Analysis ---
    print(f"\n{'='*60}")
    print(f"Stage 1: Analysing {len(articles)} article(s) collectively...")
    print(f"{'='*60}")
    post_plans = run_analysis(client, articles)
    print(f"  → Gemini decided to write {len(post_plans)} post(s).\n")

    # --- Stage 2: Writing ---
    print(f"{'='*60}")
    print(f"Stage 2: Writing {len(post_plans)} post(s)...")
    print(f"{'='*60}\n")

    manifest = []
    for i, plan in enumerate(post_plans, 1):
        print(f"Post {i}/{len(post_plans)}: {plan['suggested_title'][:60]}")

        # Gather relevant articles for this post
        source_issue_numbers = plan.get("source_issue_numbers", [])
        relevant = [articles_by_issue[n] for n in source_issue_numbers if n in articles_by_issue]
        if not relevant:
            # Fallback: use all articles
            relevant = articles

        markdown_text = run_writing_pass(client, plan, relevant, today)

        # Determine slug
        title = extract_frontmatter_title(markdown_text)
        base_slug = slugify(title) or slugify(plan["suggested_title"])
        slug = unique_slug(base_slug)

        # Write draft file
        draft_path = os.path.join(DRAFTS_DIR, f"{slug}.md")
        with open(draft_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        print(f"  ✓ Draft written: {draft_path}\n")

        manifest.append({
            "slug": slug,
            "draft_path": draft_path,
            "suggested_title": plan["suggested_title"],
            "source_issue_numbers": source_issue_numbers,
        })

    # Write manifest for downstream scripts
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ {len(manifest)} draft(s) written. Manifest at {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
