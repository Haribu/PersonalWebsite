---
description: Weekly automated blog post generation from Feedly reading queue
---

# Blog Pipeline SOP

This workflow is orchestrated by **Antigravity (Layer 2)**. All AI analysis, writing,
and image generation happens locally in the Antigravity session — no external API keys
required. The execution scripts (Layer 3) handle deterministic tasks only.

## When to Run

Trigger manually by saying `/generate_blog_post` or "generate this week's blog posts".
A reminder issue will be created every Sunday at 18:00 BST if articles are queued.

## Inputs

- **GitHub Issues** labelled `blog-queue` created automatically by Zapier from the
  Feedly "Writting Input" board. Each issue contains:
  - Article URL
  - Feedly article content (body text, where available)
  - Harry's highlight (key passage he found significant)
  - Harry's note (his initial reaction)
  - Any additional comments Harry added to the issue manually

## Step-by-Step Execution

### Step 1 — Fetch the queue
```bash
python execution/fetch_queue.py
```
Reads all open `blog-queue` issues. Writes `.tmp/queue.json`.
If output is an empty list, report "No articles queued" and stop.

### Step 2 — Scrape and enrich articles
```bash
python execution/scrape_article.py
```
Enriches each article with full body text. Uses Feedly content if substantial (>500 chars);
falls back to scraping the URL via trafilatura. Writes `.tmp/articles.json`.

### Step 3 — Analysis checkpoint (Antigravity does this directly)

Read `.tmp/articles.json` in full. For each article, review:
- Full article text
- Harry's highlight (what he found most significant)
- Harry's note (his initial reaction / angle)
- Any manual comments on the GitHub Issue

Perform a collective analysis across all articles:
1. How many distinct blog posts should be written? (Cap: 3)
2. For each post: what is the central argument, which articles inform it, what is Harry's angle?
3. What named phenomenon should anchor the post?

**Present this analysis to Harry before writing anything.** Example:
> "I'm planning 2 posts this week:
> 1. *AI Governance Liability* — combining articles 1 and 3, leading with your ISO 42001 highlight...
> 2. *LLM Supply Chain Attacks* — article 2 standalone, angle from your 'this is the new firmware' note...
>
> Article 4 is paywalled (metadata only) — I'd skip it. Happy to proceed?"

Wait for confirmation. Adjust angles if redirected.

### Step 4 — Write drafts (Antigravity does this directly)

For each decided post, write a complete draft using `write_to_file` to:
`.tmp/drafts/<slug>.md`

Follow the authorial voice brief below in full. Include valid frontmatter.

### Step 5 — Generate header images (Antigravity does this directly)

Use the `generate_image` tool for each post. Derive a specific visual subject from
the post title and summary. Apply the standard style defined below.

Save to: `.tmp/drafts/header_<slug>.png`

### Step 5.5 — Author Draft Manifest (Antigravity does this directly)

You MUST create `.tmp/draft_manifest.json` so the staging script knows how to link the drafts with source issue numbers. Use this schema list:
```json
[
  {
    "slug": "synthetic_authority_vulnerability",
    "suggested_title": "The Milgram Trap",
    "draft_path": ".tmp/drafts/synthetic_authority_vulnerability.md",
    "image_path": ".tmp/drafts/header_synthetic_authority_vulnerability.png",
    "source_issue_numbers": [14, 15]
  }
]
```

### Step 6 — Stage and validate
```bash
python execution/stage_blog_posts.py
```
Validates frontmatter, patches `{{ base_url }}` image references, confirms all files
are in place. Aborts loudly if any post fails validation.

### Step 7 — Publish to GitHub and Clean Up
```bash
python execution/publish_blog_posts.py
```
This script automates the final pipeline actions:
1. Creates a local git branch for the weekly batch.
2. Stages the generated blog contents.
3. Commits and pushes the branch to remote.
4. Creates a Pull Request with a dynamically generated description.
5. Updates all source issues (comments with the PR link, labels as `blog-processed`, and closes them).

---

## Harry McLaren — Authorial Voice Brief

This brief governs every writing pass. Follow it precisely.

### Role & Framing
Harry McLaren is Head of Cyber Defence. His intellectual territory is the **"Collision Space"** —
the intersection of emerging AI capability and established security frameworks (NIST CSF,
ISO 27001, NIST AI RMF). He is not an academic. He is a practitioner who reads widely
and synthesises from operational experience.

### Tone
- Direct and analytical. Assertive, not arrogant.
- Conversational but precise — as if briefing a senior peer, not writing a journal paper.
- **Names phenomena.** Coins terms for specific dynamics (e.g. "Context Rot", "Synthetic
  Authority", "Epistemic Capture"). Named phenomena make ideas portable and memorable.
- Comfortable challenging consensus. Includes adversarial critique perspectives.
- Never breathless or hyperbolic. Never uses: "in conclusion", "it is important to note",
  "game-changer", "paradigm shift", "unprecedented", "navigate".

### Structure
1. **Hook paragraph** — a sharp observation or reframe. Do NOT restate the title.
2. **Named phenomenon** — coin or invoke a specific term for the central problem.
3. **2–4 `###` subheadings** — each covering a distinct analytical angle.
4. **Adversarial / Critical section** — steelman the counterargument or failure mode.
   Title: *"The Red Team Perspective"* or *"Critical Review & Failure Points"*.
5. **Concrete recommendations** — numbered list. Specific, operational. Not generic.

### Style Rules
- `**Bold**` key terms on first use.
- `*Italics*` sparingly for emphasis only.
- Cite sources inline: `"...as argued in [this CirriusTech analysis](URL)..."`
- "Recommended Reading" section only if 2+ sources genuinely merit it.
- Avoid passive voice. Avoid hedging phrases.
- **Target: 700–900 words.** Do not pad.

### Harry's Annotations Are First-Class Input
- **Highlight** = passage Harry found most significant → make it structurally central
- **Note** = Harry's initial reaction → use it to orient the post's angle
- **Issue comments** = additional thoughts → incorporate them

---

## Frontmatter Schema

```yaml
---
title: "Post Title Here"
date: "YYYY-MM-DD HH:MM:SS"
summary: "A single punchy sentence. Under 160 characters."
---
```

`date` = date the batch is run. Do not include `category`, `external_link`, or `featured`.

## Slug / Filename Convention

- Lowercase, underscores, no special characters. Max 50 chars.
- Example: "The Milgram Trap..." → `synthetic_authority_vulnerability`
- Check `website/content/blog/` for collisions before finalising.

## Image Style Guide

Prompt template for `generate_image`:
> *"[SPECIFIC VISUAL SUBJECT derived from post theme]. Dark cinematic abstract digital
> composition. Deep navy and dark teal colour palette with subtle electric blue highlights.
> Dramatic directional lighting. Ultra-detailed, photorealistic render. No text, no
> typography, no logos, no watermarks, no human faces. Wide landscape aspect ratio."*

Derive `[SPECIFIC VISUAL SUBJECT]` from the post theme — e.g.:
- AI governance → "Network of interconnected governance nodes with data flows"
- Supply chain attack → "Fractured binary code cascading through an industrial pipeline"
- Data poisoning → "Abstract contaminated data streams entering a machine learning grid"

---

## Edge Cases

| Situation | Behaviour |
|---|---|
| No issues in queue | Report "No articles queued" and stop. Do not create branch or PR. |
| Article URL is paywalled | Use Feedly content. Log warning. Ask Harry if he wants to paste full text. |
| Gemini decides 4+ posts | Cap at 3. Note remaining articles in the PR body as "carried over". |
| Frontmatter validation fails | Skip that post, continue with others. Report clearly in PR body. |
| Image generation fails | Stage post without image. Note in PR body. |

---

## Learning Log

_Update this section after each run to capture API limits, timing, edge cases, or
prompt improvements discovered._

| Date | Issue | Fix Applied |
|---|---|---|
| 2026-04-04 | PR failed due to repo PR toggle disabled | Enabled pull requests inside repo settings via API. |
| 2026-04-04 | PR failed due to invalid assignee | Changed `--assignee harrymclaren` to `--assignee "@me"`. |
