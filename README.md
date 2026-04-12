# Harry McLaren — Personal Website

This repository contains the source code for [Harry McLaren's](https://harrymclaren.co.uk) highly performant, static personal website. It simultaneously serves as the host repository for a **3-Layer AI Agent Architecture**, allowing autonomous and semi-autonomous AI systems to securely build, manage, and maintain the codebase.

## 🌟 Key Features

As a Head of Cyber Defence and Strategic Advisor, the technical foundation of this site mirrors professional priorities: security, speed, accessibility, and modern aesthetics.

- **Security-First Architecture**: Enforces a strict, dynamic Content Security Policy (CSP) with automated SHA-256 script hashing. The production environment is built on a **Hardened Unprivileged Nginx** foundation, enforcing non-root execution (UID 101) to minimize attack surface.
- **Automated Verification**: GitHub Actions automatically audits every build via a custom cryptographic verifier (`verify_build.py`), TruffleHog (Secrets), and Bandit (Python SAST).
- **Accessibility & UX Foundation**: Natively supports Dark/Light mode segmentation, an integrated Dyslexic-Friendly Font switch, and dynamic global text scaling (90% - 140%), fully persisted via local storage. Everything is keyboard and screen-reader navigable.
- **Technical SEO Optimized**: Automatically builds `sitemap.xml` and `robots.txt` on compilation. Dynamically injects deeply structured `JSON-LD` schemas (Person & BlogPosting) and OpenGraph/Twitter Cards for perfect social media rendering. 

---

## 🏗️ The 3-Layer AI Architecture

This repository is engineered to be collaboratively operated by AI agents (like Claude or Gemini). To bridge the gap between probabilistic Large Language Models and deterministic code infrastructure, the AI operations are split into three layers:

1. **Layer 1: Directive (Intent)**
   - Living Standard Operating Procedures (SOPs) residing in the `.agents/workflows/` directory.
   - Natural language instructions that dictate agent boundaries, inputs, tools, and edge cases.
2. **Layer 2: Orchestration (Decision Making)**
   - The AI Agent environment context. The AI reads directives intelligently, routes functionality through specialized `skills/` (like the `UX_Skill` or `PM_Skill`), and plans implementations autonomously.
3. **Layer 3: Execution (Deterministic Output)**
   - Hardcoded Python routines residing in the `execution/` directory. 
   - The AI writes or utilizes deterministic scripts (like `build_site.py`) to systematically and safely apply changes across the site without hallucinating logic loops.

For more details on interacting with the architecture as an agent, please reference [`ai.md`](ai.md).

---

## 🌐 Directory Structure

* `.agents/` - Automated workflows and living SOPs (Layer 1 Directives) to orchestrate agent operations.
* `.github/` - GitHub Actions workflows for continuous integration, security scanning, and deployment straight to GitHub Pages.
* `execution/` - Core Python engine scripts (`build_site.py` for SSG compilation, `verify_build.py` for CSP cryptographic auditing).
* `skills/` - Extensible Agent personas guiding specialized execution (PM, UX, Optimization, etc.).
* `website/` - The core frontend interface.
  * `assets/` - Static assets, organised into subdirectories for clarity and scale:
    * `site/` - CSS, JavaScript, and fonts (global design system and UI logic).
    * `brand/` - Logos and favicons.
    * `profile/` - Personal documents (CV, resume).
  * `content/` - YAML data models (`career.yaml`, `showcase.yaml`) and folder-based blog posts (each post lives in its own `content/blog/<slug>/` folder alongside its images).
  * `templates/` - Jinja2 HTML templates used to dynamically scaffold the pages.
  * `public/` - **DO NOT EDIT.** The auto-generated immutable build folder containing the final static HTML output.
* `.tmp/` - Temporary intermediate files generated during execution. Never committed, always regenerated.
* `.env`, `credentials.json`, `token.json` - Environment variables and API credentials.

---

## 📝 Content Management Guide

The website's data is heavily abstracted from the HTML, allowing for instantaneous, painless updates. 

### 1. Updating the Timeline or Showcase
The **Career** and **Showcase** pages are powered by structured YAML payloads. Simply copy, paste, and edit these blocks inside `website/content/`.

**Example `career.yaml` entry:**
```yaml
- title: "Head of Cyber Defence"
  company: "CyberCorp"
  logo: "logo_cybercorp.png" # Place image inside website/assets/brand/
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

### 2. Adding a Company Logo
Drop the logo image into `website/assets/brand/` and reference it by filename in `career.yaml` or `showcase.yaml`.

### 3. Drafting a New Blog Post
Blog posts use a **folder-based structure** — each post lives in its own directory under `website/content/blog/<slug>/`.

**The fastest way** is to use the scaffold script from the `website/` directory:
```bash
python new_post.py "My Post Title" --summary "A short summary."
```
This creates `website/content/blog/my-post-title/index.md` pre-populated with frontmatter.

Alternatively, create the folder and file manually:
1. Create a folder: `website/content/blog/my-post-title/`
2. Create `index.md` inside it with the YAML frontmatter:
```markdown
---
title: "Title of your Transmission"
date: "YYYY-MM-DD HH:MM:SS"
summary: "A short 1-2 sentence description for the transmission log feed."
---

![Post header image](./header.png)

Write your markdown content here...
```
3. Drop your header image into the same folder as `header.png`.

At build time, the Python engine will:
- Copy `header.png` to `public/assets/blog/<slug>/header.png`
- Resolve the `./header.png` reference to the correct public URL
- Estimate reading time, extract the thumbnail, inject Schema.org JSON, and compile the HTML

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