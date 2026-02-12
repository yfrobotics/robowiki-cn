# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chinese-language robotics wiki (云飞机器人中文维基) built with MkDocs and the Material theme. Content covers control systems, sensing, computer vision, planning, machine learning, simulation, ROS, Linux, RTOS, hardware, and robotics industry databases. Licensed under CC 4.0-BY-SA.

## Build Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Local development server (localhost:8000)
mkdocs serve

# Build static site to site/ directory
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Architecture

- **`mkdocs.yml`** — Primary config: site metadata, navigation tree, theme, markdown extensions. The `nav:` section defines the full site structure and must be updated when adding/removing pages.
- **`docs/`** — All markdown content and assets. Each topic area has its own subdirectory (e.g., `control/`, `simulation/`, `ros/`).
- **`docs/_static/`** — Custom CSS (`css/extra.css`) and JS (`js/mathjaxhelper.js`) loaded by MkDocs.
- **`site/`** — Build output (gitignored).
- **`.github/workflows/main.yml`** — CI/CD: builds and deploys to GitHub Pages on push/PR to main.

## Content Conventions

- **File naming**: English, lowercase, hyphen-separated (e.g., `path-planning.md`).
- **Images**: Store in an `assets/` subdirectory next to the markdown file. Keep source files (`.vsx`, `.drawio`) alongside exported images.
- **Headings**: Maximum 4 levels (`#` through `####`).
- **Spacing**: Two blank lines between same-level paragraphs in source. Trailing blank line at end of file.
- **Math**: Inline `\(...\)`, display `$$ ... $$` (rendered via MathJax).
- **Admonitions**: Use `!!! note "引言"` blocks for introductions.
- **Citations**: Non-original images need attribution. References go in a "参考资料" section at article end.
- **Language**: Chinese content. Avoid internet slang. Spell out abbreviations on first use.

## Adding a New Article

1. Create the `.md` file in the appropriate `docs/` subdirectory.
2. Add the file path to the `nav:` section in `mkdocs.yml`.
3. Place any images in an `assets/` folder next to the markdown file.

## Key Dependencies

- `mkdocs` + `mkdocs-material` — Site generation and Material theme
- `python-markdown-math` + MathJax CDN — LaTeX math rendering
- `pymdown-extensions` — Enhanced code highlighting (`pymdownx.highlight`, `pymdownx.superfences`)
