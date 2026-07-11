# GitHub Profile README Design

## Overview

This document defines the design for the `deserveto/deserveto` GitHub profile repository. The goal is to create a clean, professional, and maintainable profile README that presents Fikri Tri Wibowo as a balanced Information Technology student with cybersecurity as the strongest theme, while also showing work in AI/ML, networking, cloud infrastructure, and software development.

## Goals

- Present a professional first impression without an excessive hacker aesthetic.
- Use a minimal, neutral, monochrome visual system.
- Keep animation limited to the ASCII portrait and contribution graph.
- Highlight both public repositories and important work without public repository links.
- Make the profile maintainable through local generation scripts and a daily GitHub Action.
- Never commit the original portrait photo.

## Profile Structure

### 1. Hero section

The first section contains:

- Animated ASCII portrait generated from the provided photo.
- A matching information card.
- Name: **Fikri Tri Wibowo**.
- Tagline: **Information Technology Student · Cybersecurity · AI/ML · Software Development**.
- Contact buttons for LinkedIn and Instagram.

Contact destinations:

- LinkedIn: `https://www.linkedin.com/in/fikri-tri-wibowo-446034296/`
- Instagram: `https://www.instagram.com/fikritw_`

### 2. About Me

Approved copy:

> I am an Information Technology student at Telkom University with a strong interest in cybersecurity, artificial intelligence, networking, cloud infrastructure, and software development. I enjoy building practical systems, exploring security problems, and applying machine learning to real-world challenges.

### 3. Featured Projects

The featured-project section contains four projects:

1. **PhishGNN-EEF**  
   Research on phishing website detection using Graph Neural Networks with enhanced edge features on hyperlink graphs.

2. **VulnScan Toolkit**  
   A lightweight cybersecurity toolkit for vulnerability scanning and security assessment. Link to the public repository when available.

3. **ZipLift**  
   A desktop archive-management utility focused on simple and efficient file extraction. Link to the public repository.

4. **Azure VM Portfolio**  
   A portfolio deployed on an Ubuntu virtual machine using Apache, PHP, Git, and firewall configuration. Link only when a public deployment or repository is available.

Projects without public links remain visible as highlighted work rather than being omitted.

### 4. Technology Stack

The stack is grouped into readable categories instead of a large undifferentiated badge wall.

- **Languages:** Python, JavaScript, TypeScript, PHP, Java, C++
- **AI/ML:** PyTorch, PyTorch Geometric, Graph Neural Networks, scikit-learn
- **Web:** Laravel, Next.js, HTML, CSS, Tailwind CSS
- **Cloud and infrastructure:** Azure, Google Cloud, Linux, Apache
- **Security and networking:** vulnerability assessment, phishing detection, Wireshark, Packet Tracer
- **Tools:** Git, GitHub, Docker, VS Code

### 5. Contribution Graph

The contribution graph is rendered as a restrained monochrome animated SVG. A daily GitHub Action refreshes public contribution data and commits the updated SVG.

### 6. Contact

The final section repeats the principal contact options:

- GitHub
- LinkedIn
- Instagram

## Visual Direction

- Minimal professional appearance.
- Neutral grayscale palette.
- Clean spacing and subtle borders.
- No rainbow effects, glitch effects, or aggressive cyber styling.
- No excessive badge collections.
- Portrait and information card should have visually matched dimensions.
- Animation is limited to the portrait reveal and contribution-graph reveal.
- The README must remain readable in GitHub light and dark themes.

## Repository Layout

```text
README.md
avi-ascii.svg
info-card.svg
contrib-heatmap.svg

scripts/
  fetch_contributions.py
  render_heatmap_svg.py
  make_ascii_svg.py
  make_info_card.py
  requirements.txt

data/
  contributions.json

.github/workflows/
  update-profile-art.yml

docs/superpowers/specs/
  2026-07-11-github-profile-design.md
```

The original portrait photo is used only during generation and is never committed.

## Data Flow

1. The uploaded portrait is processed locally in the ChatGPT execution environment.
2. The portrait generator creates `avi-ascii.svg`.
3. The information-card script creates `info-card.svg` from approved profile content.
4. The contribution-fetch script requests only the public GitHub contribution page for `deserveto` and stores normalized data in `data/contributions.json`.
5. The heatmap renderer creates `contrib-heatmap.svg`.
6. The README references the generated assets using relative repository paths.
7. GitHub Actions refreshes only the contribution data and heatmap on its daily schedule.

## Security and Privacy

- Do not commit the original portrait image.
- Do not store GitHub tokens, secrets, cookies, SSH keys, or local environment files.
- Do not request private contribution data.
- Use only GitHub-provided `GITHUB_TOKEN` inside the workflow.
- Give the workflow only the minimum required permission: `contents: write`.
- Do not use shell downloads, obfuscated commands, `eval`, or remote execution.
- Use patched dependencies, including `requests>=2.32.4`.
- Pin GitHub Actions to stable major versions and keep the workflow small and auditable.

## Error Handling

- The contribution fetcher must fail with a clear message when GitHub returns an unsuccessful response.
- Generated JSON must be validated before rendering.
- Renderers should create deterministic output for the same input.
- The workflow should avoid creating commits when generated output has not changed.
- Missing optional project links must not break README rendering.
- If the contribution refresh fails, the existing graph remains in the repository.

## Testing and Verification

Before publishing:

- Run all Python scripts in an isolated virtual environment.
- Check scripts for syntax errors.
- Confirm generated SVG files are valid XML.
- Inspect SVGs for external scripts, remote image references, or unsafe embedded content.
- Confirm the original portrait does not appear in the repository tree.
- Verify every README link.
- Confirm the README renders correctly on the GitHub profile page.
- Review the GitHub Actions workflow before enabling repository write permissions.
- Trigger the workflow manually and verify that it changes only the expected contribution files.

## Acceptance Criteria

The design is complete when:

- The profile repository renders a polished README on the `deserveto` GitHub profile.
- The hero area contains the animated ASCII portrait and matching information card.
- The approved About Me copy, four featured projects, grouped stack, and contact links are present.
- LinkedIn and Instagram links point to the approved destinations.
- The contribution graph updates through a small, reviewed daily workflow.
- No original photo, credential, private data, or unnecessary dependency is committed.
- The result remains professional, readable, and maintainable.
