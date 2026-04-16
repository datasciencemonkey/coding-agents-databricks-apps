# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Workshop materials for a 6.5-hour Coles Group vibe coding hackathon (9:30 AM – 4:00 PM). Teams of 2-3 build a Grocery Intelligence Platform using AI coding agents on Databricks. Three parallel tracks: Data Engineering, Data Science, and Analyst.

## Build & Export Commands

```bash
# Generate shareable PDFs from track HTML workbooks (requires Node.js)
npm install puppeteer pdf-lib --silent
cp ~/.claude/plugins/cache/fe-vibe/fe-html-slides/*/skills/html-slides/resources/export-pdf.js .
node export-pdf.js track-common.html   # → track-common.pdf
node export-pdf.js track-de.html       # → track-de.pdf
node export-pdf.js track-ds.html       # → track-ds.pdf
node export-pdf.js track-analyst.html  # → track-analyst.pdf

# Run reference implementation tests (requires PySpark)
cd reference-implementation && uv run pytest tests/test_pipeline.py -x --no-header -q
cd reference-implementation && uv run pytest tests/test_quality.py -x --no-header -q
cd reference-implementation && uv run pytest tests/test_app.py -x --no-header -q
```

## Workshop Schedule (9:30–16:00)

- **9:30** Welcome + Icebreaker (15 min)
- **9:45** Theory: Vibe Coding, CLAUDE.md, TDD (45 min)
- **10:30** Break (15 min)
- **10:45** Lab 0: Guided Hands-On — ALL together (45 min)
- **11:30** Theory: Skills, MCP, Genie/AI-BI (20 min)
- **11:50** Track Briefing — teams choose DE / DS / Analyst (10 min)
- **12:00** Lab 1 — track-specific (60 min)
- **13:00** Show & Tell (15 min)
- **13:15** Lunch (45 min)
- **14:00** Lab 2 — track-specific (60 min)
- **15:00** Team Demos (30 min)
- **15:30** Takeaways + Close (15 min)

## Six Files Must Stay In Sync

When changing workshop content, update all six:
1. `slides.html` — the deck attendees see
2. `slides-facilitator.html` — same deck with speaker notes (JS-injected from `data-notes` attributes)
3. `FACILITATOR-SCRIPT.md` — dot-point cue cards per slide
4. `WORKSHOP-PLAN.md` — master plan with session details and timing
5. `VIBE-CODING-GUIDE.md` — markdown version of common track theory content
6. `track-common.html` — HTML workbook version of the same content

The three track HTMLs (`track-de.html`, `track-ds.html`, `track-analyst.html`) pull content from the corresponding lab markdown files (`LAB-1-DE.md`, `LAB-2-DE.md`, etc.) and must stay aligned with them.

## Slide Deck Conventions

Single HTML files with no build step. Open directly in a browser.

**Slide structure:** Each slide is a `<section class="slide">` with `aria-label` (title) and `data-notes` (speaker notes). Follow the `<!-- SLIDE N: TITLE -->` comment convention.

**CSS variables:** Databricks brand in `:root` — `var(--db-lava)` #FF3621, `var(--db-navy)` #1B3139, `var(--db-teal)` / `var(--db-green)` #00A972, `var(--db-oat)` #F9F7F4. Coles red `var(--coles-red)` #E01A22 used sparingly.

**Code blocks:** `<div class="code-block">` with `<span class="keyword|string|comment|function|type|decorator">` for syntax highlighting. `white-space: pre` — preserve indentation in HTML source.

**PDF export:** Uses Puppeteer to screenshot each `.slide` section at 1920×1080 @2x, then pdf-lib stitches into PDF. This is why all exportable HTML files must use `<section class="slide">` elements.

## Track Workbook Conventions

The `track-*.html` files are slide-format workbooks (not presentation decks). Each uses the same `.slide` structure for PDF export compatibility but styled as document pages with:
- `.cover-slide` — dark themed title page
- `.divider-slide` — section dividers with timing badges
- `.page-slide` — white content pages with `.page-header`, `.page-content`, `.page-footer`

Track accent colors: DE = lava red (#FF3621), DS = purple (#7c3aed), Analyst = cyan (#0891b2), Common = green (#00A972).

## Three-Track System

After shared theory and Lab 0, teams choose one track:

| Track | Badge Color | Lab 1 | Lab 2 | Lab Files |
|-------|------------|-------|-------|-----------|
| Data Engineering | Red | Lakeflow pipeline (Bronze→Silver→Gold) | Data quality, FSANZ source, scheduling | `LAB-1-DE.md`, `LAB-2-DE.md` |
| Data Science | Purple | Feature engineering, MLflow experiments | Model training, serving, prediction app | `LAB-1-DS.md`, `LAB-2-DS.md` |
| Analyst | Cyan | Genie spaces, AI/BI dashboards | FastAPI web app with embedded dashboards | `LAB-1-ANALYST.md`, `LAB-2-ANALYST.md` |

The original generic lab files (`LAB-1-DATA-PIPELINE.md`, `LAB-2-APP-GENIE-DASHBOARD.md`) are kept for reference but the track-specific versions are canonical.

## Reference Implementation

`reference-implementation/` contains the complete DE track solution built following Anthropic best practices (CLAUDE.md → tests → implementation). It serves as the facilitator answer key and teaching artifact. 55 tests across three files: `test_pipeline.py` (bronze/silver/gold), `test_app.py` (FastAPI), `test_quality.py` (data validation). Pipeline uses `import databricks.declarative_pipelines as dp` with `@dp.table` decorators and `@dp.expect` / `@dp.expect_or_fail` quality rules.

## Content Alignment

The workshop references a working implementation at `~/Repos/coles-genie-demo` — a Databricks Asset Bundle with Lakeflow pipelines ingesting ABS Retail Trade, ABS CPI Food, FSANZ Food Recalls, and ACCC Grocery PDFs. Lab instructions, slide content, and pipeline flow diagrams must stay aligned with that repo's actual data sources, table names, and schemas.
