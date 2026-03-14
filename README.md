# Harry McLaren - Personal Website & AI Orchestration System

This repository contains the source code for Harry McLaren's static, markdown-powered personal website, as well as the 3-Layer AI Agent Architecture used to collaboratively build, manage, and maintain it. 

## Project Overview

The project is split into two main components:
1. **The Website (`website/`)**: A highly performant, static, markdown-powered web application built with a strict Content Security Policy.
2. **The AI Architecture**: A system that separates intent (Layer 1) from decision-making (Layer 2) and deterministic execution (Layer 3), allowing AI agents to systematically manage and update the repository.

---

## 🏗️ 3-Layer AI Architecture

This repository is designed to be operated by AI agents within a reliable framework to maximize consistency while manipulating the code and content. The mismatch between probabilistic LLMs and deterministic business logic is bridged via:

* **Layer 1: Directive (What to do)**
  - Living Standard Operating Procedures (SOPs) residing in the `directives/` directory.
  - Natural language instructions that define agent goals, inputs, tools, and edge cases (e.g., `cyber_skill.md`, `dev_skill.md`, `pm_skill.md`, `ux_skill.md`).
* **Layer 2: Orchestration (Decision making)**
  - This is the AI Agent environment (Claude, Gemini, etc.).
  - The AI reads directives, performs intelligent routing, calls execution scripts, and updates directives as it learns.
* **Layer 3: Execution (Doing the work)**
  - Deterministic Python scripts residing in the `execution/` directory.
  - Contains reliable, testable data processing tools, API handlers, etc., reducing compound errors.

For more details on interacting with the architecture as an agent, please read [`ai.md`](ai.md).

---

## 🌐 The Website (`website/`)

The core personal website is generated via a custom static site generator, maintaining a zero-dependency, lightweight footprint.

* **Security First:** Strict Content Security Policy (CSP), no backend databases.
* **Performance:** Minimalist vanilla CSS, no heavy modern JS framing.
* **Ease of Use:** Content is entirely driven by Markdown frontmatter files located in `website/content/blog/`.

### Building & Running Local Website
The site is generated using a custom Python script:
```bash
# Move into the website directory
cd website

# Rebuild the templates and markdown to public/
python build_site.py

# To write a new blog post
python new_post.py "My New Post" -s "A quick summary"
```

The output is emitted to `website/public/`, which is fully static and ready for hosting. 

For full instructions on updating content or maintaining the website, see the [Website README](website/README.md).

---

## 📂 Directory Structure

* `.github/` - GitHub Actions CI/CD workflows for automatic deployment and security analysis (Dependabot enabled).
* `.tmp/` - Temporary execution files used during AI processing. (Not committed)
* `directives/` - Markdown SOPs for AI tools and workflows (Layer 1).
* `execution/` - Python scripts representing deterministic tools (Layer 3).
* `website/` - The static website source, templates, CSS, and markdown content.
  * `build_site.py` - Custom static site generator.
  * `.well-known/` - Contains the standard `security.txt` configuration.
  * `public/` - The published artifacts ready for deployment.

---

## 🚀 CI/CD & Deployment

Changes pushed to the `main` branch automatically trigger `.github/workflows/deploy.yml` which rebuilds the static output using `build_site.py` and deploys it directly to **GitHub Pages**.

Security tests (Trufflehog secret scanning) are also executed via GitHub actions upon push (`security.yml`). Dependencies and Actions are strictly pinned via SHA hashes and `requirements.txt` to mitigate supply-chain attacks.