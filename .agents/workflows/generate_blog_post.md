---
description: Weekly automated blog post generation from Feedly reading queue
---

# Blog Pipeline SOP

This workflow governs the automated weekly blog post generation pipeline.
It runs every Monday at 07:00 UTC via `.github/workflows/weekly_blog_batch.yml`.

## Inputs

- **GitHub Issues** labelled `blog-queue` created by Zapier from the Feedly "Writting Input" board
- Each issue contains: article URL, Feedly article content, Harry's highlight, Harry's note
- Issue comments may contain additional thoughts added manually before the batch runs

## Outputs

- 1 or more markdown posts in `website/content/blog/<slug>.md`
- 1 header image per post in `website/assets/header_<slug>.png`
- A single Pull Request on branch `draft/weekly-batch-YYYY-MM-DD`

## Script Execution Order

1. `execution/fetch_queue.py` — fetch all open blog-queue issues from the past 8 days
2. `execution/scrape_article.py` — enrich articles with full text if Feedly content is thin
3. `execution/generate_blog_drafts.py` — Gemini analysis + writing pass
4. `execution/generate_blog_images.py` — Imagen 4 header per post
5. `execution/stage_blog_posts.py` — validate and place files for commit

If `fetch_queue.py` finds no queued issues, exit cleanly. Do not create a PR or branch.

---

## Harry McLaren — Authorial Voice Brief

This brief is the ground truth for the Gemini writing prompt. It must be embedded verbatim in the system prompt of `generate_blog_drafts.py`. Update this section if the voice evolves.

### Role & Framing
Harry McLaren is Head of Cyber Defence. His intellectual territory is the "Collision Space" — the point where emerging AI capability meets established security frameworks (NIST CSF, ISO 27001, NIST AI RMF). He is not an academic. He is a practitioner who reads widely and synthesises from operational experience.

### Tone
- Direct and analytical. Assertive, not arrogant.
- Conversational but precise — as if briefing a senior peer, not writing a journal paper.
- Willing to name things. Coins terms for phenomena (e.g. "Context Rot", "Synthetic Authority", "Epistemic Capture").
- Comfortable challenging consensus. Includes "devil's advocate" or adversarial critique perspectives.
- Not breathless or hyperbolic. Never uses phrases like "in conclusion", "it is important to note", or "game-changer".

### Structure
Every post follows this loose shape:
1. **Hook paragraph** — a sharp observation or reframe of the source material. No headline-restating the title.
2. **Named phenomenon** — coin or invoke a specific term for the problem being discussed.
3. **2–4 `###` subheadings** — each covering a distinct analytical angle.
4. **Adversarial / Critical section** (often titled "The Red Team Perspective" or "Critical Review") — steelman the counterargument or failure mode.
5. **Concrete recommendations** — numbered list, actionable, specific. Not generic "patch your systems" advice.

### Style Rules
- Use `**Bold**` to introduce key terms on first use.
- Use `*italics*` sparingly for emphasis, never for decoration.
- Cite sources inline as hyperlinks naturally woven into prose: `"...as argued in [this CirriusTech analysis](URL)..."`
- Include a "Recommended Reading" section at the end only if 2+ external sources are genuinely worth citing beyond the source article.
- Avoid passive voice. Avoid hedging phrases ("it could be argued", "one might say").
- Target length: **700–900 words**. Quality over length. Do not pad.

### Harry's Annotations Are First-Class Input
When a highlight or note is provided from Harry's Feedly annotations, treat them as editorial direction:
- **Highlight** = the passage Harry found most significant. Make it structurally important to the post.
- **Note** = Harry's initial reaction or angle. Use it to orient the post's perspective.
- **Issue comments** = additional thoughts added before the batch run. Incorporate them.

---

## Frontmatter Schema

Every generated post must include valid frontmatter matching this exact schema:

```yaml
---
title: "Post Title Here"
date: "YYYY-MM-DD"
summary: "A single punchy sentence summarising the post's argument. Under 160 characters."
---
```

The `date` field must be the date the batch workflow runs (today's date in the Actions environment).
Do not include `category`, `external_link`, or `featured` fields — these are manually curated.

---

## Slug / Filename Convention

- Derived from the post title: lowercase, words separated by underscores, no special characters
- Example: "The Milgram Trap: Why Synthetic Authority..." → `synthetic_authority_vulnerability`
- Maximum 50 characters
- Must be unique — check `website/content/blog/` before finalising

## Image Convention

- Filename: `header_<slug>.png`
- Dimensions: landscape, generated at default Imagen 4 aspect ratio (~16:9 internally, saved as PNG)
- Style: dark, abstract, cinematic, cybersecurity/AI themed — no text, no logos, no people's faces
- See `generate_blog_images.py` for the full prompt template

---

## Edge Cases

| Situation | Behaviour |
|---|---|
| No issues in queue | Exit cleanly. Log "No articles queued this week." Do not create branch or PR. |
| Article URL is paywalled / returns 403 | Use Feedly content from the issue body. Log warning. Do not skip the article. |
| Gemini decides all articles belong in one post | Generate a single synthesised post. Fine. |
| Gemini decides 4+ posts from one week | Cap at 3 posts per batch run. Carry over remaining issues (remove `blog-queue` label, re-add it next week). |
| `lint_content.py` fails on a draft | Log the error, skip that post, continue with remaining. Report failure in PR body. |
| Image generation fails | Stage the post without an image. Add a note to the PR body. The post template handles missing images gracefully. |

---

## Learning Log

_Update this section when the self-annealing loop discovers issues._

| Date | Issue | Fix Applied |
|---|---|---|
| — | — | — |
