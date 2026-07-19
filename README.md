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
*   `assets/` - Static assets, organised into subdirectories for clarity and scale:
    *   `site/` - CSS, JavaScript, and fonts (global design system and UI logic).
    *   `brand/` - Logos and favicons.
    *   `profile/` - Personal documents (CVs, resume, LinkedIn optimizations).
*   `content/` - YAML data models (`career.yaml`, `showcase.yaml`) defining timelines, awards, and community entries.
*   `templates/` - Jinja2 HTML templates used to dynamically scaffold the pages (`index.html`, `executive.html`, `advisory.html`, `insights.html`, `contact.html`).
*   `public/` - **DO NOT EDIT.** The auto-generated immutable build folder containing the final static HTML output.

---

## 📝 Content Management Guide

The website's data is heavily abstracted from the HTML, allowing for instantaneous, painless updates. 

### 1. Updating the Timeline or Showcase
The **Executive Portfolio** and **Community & Insights** pages are powered by structured YAML payloads. Simply copy, paste, and edit these blocks inside `website/content/`.

**Example `career.yaml` entry:**
```yaml
- title: "Head of Cyber Defence"
  company: "Tesco"
  logo: "logo_tesco.svg" # Place image inside website/assets/brand/
  date: "Aug 2025 – Present"
  bullets:
    - "Direct responsibility for the unified global cyber defence function..."
```

**Example `showcase.yaml` entry:**
```yaml
- title: "Presented on Emerging Technology"
  category: "speaking" # speaking | writing | event
  featured: false
  date: "2025-10-06"
  summary: "Keynote presentation at TechCon."
```

### 2. Adding a Company Logo
Drop the logo image into `website/assets/brand/` and reference it by filename in `career.yaml` or `showcase.yaml`.

---

## 🛠️ Local Development & Deployment

Development and verification runs gracefully through Python or Docker, ensuring environment parity.

**To compile and verify the site locally:**
1. From the repository root, run the compilation script:
   ```bash
   ./venv/bin/python execution/build_site.py
   ```
2. Verify the CSP cryptographic hashes:
   ```bash
   ./venv/bin/python execution/verify_build.py
   ```
3. Serve the public directory:
   ```bash
   ./venv/bin/python -m http.server 8080 --directory website/public
   ```
4. Navigate your browser to `http://localhost:8080`.

*(Alternatively, you can run the Docker compose pipeline via `docker-compose up --build -d` if Docker is running).*

## 🚀 CI/CD & Deployment Strategy

Changes pushed to the `main` branch automatically trigger `.github/workflows/deploy.yml`. 
GitHub Actions spins up an isolated Ubuntu runner, compiles `build_site.py` into production-ready HTML, audits the repository against Bandit and Trufflehog rules to guarantee zero secret leakages, and publishes the immutable `public/` directory directly to **GitHub Pages**.