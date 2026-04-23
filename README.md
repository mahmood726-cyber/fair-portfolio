# FAIRPortfolio

FAIRPortfolio is a new standalone project built from the bundled `ResearchConstellation` snapshot.

## Why this exists

The portfolio now has packaging, provenance, interoperability, and triage layers. What it still lacks is a simple maturity surface that answers one question quickly: which parts of the snapshot already look findable, accessible, interoperable, and reusable enough to prioritise?

## What it does

- scores every indexed project on FAIR-inspired proxy components
- produces per-project F/A/I/R component scores and a 100-point total
- groups results into weak, partial, emerging, and strong bands
- shows best and weakest tiers in a static dashboard
- ships an E156 bundle for publication-facing review

## Outputs

- `fair-scores.json` - full proxy scoring table
- `data.json` and `data.js` - dashboard payloads
- `index.html` - static maturity dashboard
- `e156-submission/` - paper, protocol, metadata, and reader page

## Rebuild

Run:

`python scripts/build_fair_portfolio.py`

For a custom source file:

`python scripts/build_fair_portfolio.py --source path/to/portfolio-data.json`

## Scope note

This project is FAIR-inspired proxy scoring, not a formal FAIR certification tool. The bundled snapshot does not contain enough evidence for a full standards-grade audit, so the scores should be used for prioritisation rather than compliance claims.
