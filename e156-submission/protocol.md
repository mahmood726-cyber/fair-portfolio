Mahmood Ahmad
Tahir Heart Institute
author@example.com

Protocol: FAIRPortfolio - FAIR-Inspired Proxy Maturity Audit

This protocol describes a snapshot-first maturity study using the bundled `data-source/portfolio-data.snapshot.json` copied from `ResearchConstellation`. Eligible records are all 134 indexed projects across the 12 portfolio tiers preserved in that snapshot. The primary estimand is the proportion of projects scoring at least 70/100 on a FAIR-inspired proxy scale. Secondary outputs will report mean and median total scores, weak-band prevalence, tier-level mean scores, and average component values for findable, accessible, interoperable, and reusable proxies. The build process will emit `fair-scores.json`, `data.json`, `data.js`, and a static dashboard for browser review. Component scores will use transparent proxy signals such as path specificity, delivery cues, automation cues, lifecycle normalization, and evidence of maturity rather than making formal FAIR compliance claims. Anticipated limitations include proxy misclassification, incomplete evidence in the bundled snapshot, no external URL checks, and the inability to certify FAIR compliance without richer metadata and public artifact inspection.

Outside Notes

Type: protocol
Primary estimand: proportion of projects scoring at least 70/100 on the FAIR-style proxy scale
App: FAIRPortfolio v0.1
Code: repository root, scripts/build_fair_portfolio.py, fair-scores.json, and data-source/portfolio-data.snapshot.json
Date: 2026-03-30
Validation: DRAFT

References

1. Wilkinson MD, Dumontier M, Aalbersberg IJJ, et al. The FAIR Guiding Principles for scientific data management and stewardship. Sci Data. 2016;3:160018.
2. Sansone SA, McQuilton P, Rocca-Serra P, et al. FAIRsharing as a community approach to standards, repositories and policies. Nat Biotechnol. 2019;37:358-367.
3. Sandve GK, Nekrutenko A, Taylor J, Hovig E. Ten simple rules for reproducible computational research. PLoS Comput Biol. 2013;9:e1003285.

AI Disclosure

This protocol was drafted from versioned local artifacts and deterministic build logic. AI was used as a drafting and implementation assistant under author supervision, with the author retaining responsibility for scope, methods, and reporting choices.
