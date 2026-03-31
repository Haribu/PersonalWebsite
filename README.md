# Harry McLaren — Personal Website

This repository contains the source code for [Harry McLaren's](https://harrymclaren.github.io) highly performant, static personal website. It simultaneously serves as the host repository for a **3-Layer AI Agent Architecture**, allowing autonomous and semi-autonomous AI systems to securely build, manage, and maintain the codebase.

## 🌟 Key Features

As a Head of Cyber Defence and Strategic Advisor, the technical foundation of this site mirrors professional priorities: security, speed, accessibility, and modern aesthetics.

- **Zero-Dependency SSG**: Built entirely via a custom, lightweight Python Static Site Generator (`execution/build_site.py`), ensuring blisteringly fast build times without the bloat of frontend frameworks.
- **Security-First Pipeline**: Enforces a strict Content Security Policy (CSP), with GitHub Actions automatically scanning CI/CD pipelines via TruffleHog (Secrets) and Bandit (Python SAST).
- **Accessibility & UX Foundation**: Natively supports Dark/Light mode segmentation, an integrated Dyslexic-Friendly Font switch, and dynamic global text scaling (90% - 140%), fully persisted via local storage. Everything is keyboard and screen-reader navigable.
- **Technical SEO Optimized**: Automatically builds `sitemap.xml` and `robots.txt` on compilation. Dynamically injects deeply structured `JSON-LD` schemas (Person & BlogPosting) and OpenGraph/Twitter Cards for perfect social media rendering. 

---

## 🏗️ The 3-Layer AI Architecture

This repository is engineered to be collaboratively operated by AI agents (like Claude or Gemini). To bridge the gap between probabilistic Large Language Models and deterministic code infrastructure, the AI operations are split into three layers:

1. **Layer 1: Directive (Intent)**
   - Living Standard Operating Procedures (SOPs) residing in the `directives/` directory.
   - Natural language instructions that dictate agent boundaries, inputs, tools, and edge cases.
2. **Layer 2: Orchestration (Decision Making)**
   - The AI Agent environment context. The AI reads directives intelligently, routes functionality through specialized `skills/` (like the `UX_Skill` or `PM_Skill`), and plans implementations autonomously.
3. **Layer 3: Execution (Deterministic Output)**
   - Hardcoded Python routines residing in the `execution/` directory. 
   - The AI writes or utilizes deterministic scripts (like `build_site.py`) to systematically and safely apply changes across the site without hallucinating logic loops.

For more details on interacting with the architecture as an agent, please reference [`ai.md`](ai.md).

---

## 🌐 Directory Structure

* `.agents/` - Automated workflows (e.g., local and remote deployments) to orchestrate agent operations.
* `.github/` - GitHub Actions workflows for continuous integration, security scanning, and deployment straight to GitHub Pages.
* `directives/` - Markdown SOPs defining specific agent logic.
* `execution/` - Core Python engine scripts (`build_site.py` for SSG compilation, `verify_build.py` for CSP cryptographic auditing).
* `skills/` - Extensible Agent personas guiding specialized execution (PM, UX, Optimization, etc.).
* `website/` - The core frontend interface.
  * `assets/` - CSS variable-driven design systems (glassmorphism UI) and JS UI hydration logic.
  * `content/` - YAML data models (`career.yaml`, `showcase.yaml`) and the `.md` blog archive.
  * `templates/` - Jinja2 HTML templates used to dynamically scaffold the pages.
  * `public/` - **DO NOT EDIT.** The auto-generated immutable build folder containing the final static HTML output.

---

## 📝 Content Management Guide

The website's data is heavily abstracted from the HTML, allowing for instantaneous, painless updates. 

### 1. Updating the Timeline or Showcase
The **Career** and **Showcase** pages are powered by structured YAML payloads. Simply copy, paste, and edit these blocks inside `website/content/`.

**Example `career.yaml` entry:**
```yaml
- title: "Head of Cyber Defence"
  company: "CyberCorp"
  logo: "logo_cybercorp.png" # Place image inside website/assets/
  date: "Jan 2024 – Present"
  bullets:
    - "Architected zero-trust frameworks."
```

**Example `showcase.yaml` entry:**
```yaml
- title: "Defending the Modern Enterprise"
  category: "speaking" # speaking | writing | event
  featured: true
  date: "2024-03-31" 
  external_link: "https://example.com/talk"
  summary: "Keynote presentation at CyberCon."
```

### 2. Drafting a New Blog Post
Blog posts are written purely in markdown (`.md`). 
1. Create a new markdown file inside `website/content/blog/` (e.g. `my-new-post.md`).
2. Add the YAML Frontmatter exactly to the top of the file:
```markdown
---
title: "Title of your Transmission"
date: "YYYY-MM-DD"
summary: "A short 1-2 sentence description for the transmission log feed."
category: "general"
---
Write your markdown content down here...
```
3. Commit your changes. The Python engine will dynamically estimate reading times, extract your first image as a thumbnail, wrap it in Schema.org JSON, and compile it!

---

## 🛠️ Local Development & Deployment

Development and verification runs gracefully through Docker, ensuring environment parity.

**To rebuild and preview the site locally:**
1. From the repository root, run the Docker Compose pipeline:
   ```bash
   docker-compose up --build -d
   ```
2. Navigate your browser to `http://localhost:8080`.

*(Alternatively, you can rebuild the HTML manually by executing `python execution/build_site.py` from the root directory).*

## 🚀 CI/CD & Deployment Strategy

Changes pushed to the `main` branch automatically trigger `.github/workflows/deploy.yml`. 
GitHub Actions spins up an isolated Ubuntu runner, compiles `build_site.py` into production-ready HTML, audits the repository against Bandit and Trufflehog rules to guarantee zero secret leakages, and publishes the immutable `public/` directory directly to **GitHub Pages**.