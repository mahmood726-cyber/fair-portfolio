from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "data-source" / "portfolio-data.snapshot.json"
DATA_JSON = PROJECT_ROOT / "data.json"
DATA_JS = PROJECT_ROOT / "data.js"
FAIR_SCORES_JSON = PROJECT_ROOT / "fair-scores.json"


def load_payload(source_path: Path) -> dict[str, object]:
    return json.loads(source_path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def add_points(score: int, reasons: list[str], value: int, reason: str) -> int:
    reasons.append(f"+{value} {reason}")
    return score + value


def score_findable(project: dict[str, object], text: str) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    if project["name"] and project["tierShortName"]:
        score = add_points(score, reasons, 10, "named record with tier placement")
    if project["path"] and project["path"] != "C:\\Projects\\":
        score = add_points(score, reasons, 8, "specific path rather than generic root")
    if project["statusExplicit"]:
        score = add_points(score, reasons, 7, "explicit lifecycle label present")
    return min(score, 25), reasons


def score_accessible(project: dict[str, object], text: str) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    if project["path"]:
        score = add_points(score, reasons, 5, "path recorded in the snapshot")
    if project["type"] in {"HTML app", "Static site", "Pipeline+Dashboard", "Python pipeline+HTML"}:
        score = add_points(score, reasons, 10, f"{project['type']} delivery pattern")
    if any(token in text for token in ["website", "site", "browser", "dashboard", "landing page", "showcase", "app"]):
        score = add_points(score, reasons, 5, "browser-facing access signal")
    if any(token in text for token in ["github", "api", "open", "json"]):
        score = add_points(score, reasons, 5, "distribution or interface signal")
    if project["statusExplicit"] and project["status"] not in {"paused", "archived"}:
        score = add_points(score, reasons, 5, "non-stalled explicit status")
    return min(score, 25), reasons


def score_interoperable(project: dict[str, object], text: str) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    score = add_points(score, reasons, 5, "record sits inside a structured portfolio schema")
    if project["type"] in {"Model", "Python pipeline", "Python pipeline+HTML", "Pipeline+Dashboard"}:
        score = add_points(score, reasons, 5, f"{project['type']} technical form")
    if any(token in text for token in ["api", "module", "engine", "dataset", "json", "pipeline", "extractor", "csv", "fhir", "crate"]):
        score = add_points(score, reasons, 10, "interchange or automation signal")
    if project["statusExplicit"]:
        score = add_points(score, reasons, 5, "status normalized into portfolio vocabulary")
    return min(score, 25), reasons


def score_reusable(project: dict[str, object], text: str) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    if project.get("detail"):
        score = add_points(score, reasons, 5, "descriptive project detail present")
    if any(token in text for token in ["tests", "v1.0", "v1.1", "v2.0", "manuscript", "journal", "complete", "validated", "review clean"]):
        score = add_points(score, reasons, 10, "quality or maturity signal")
    if any(token in text for token in ["tool", "suite", "module", "methods", "course", "guide", "tracker"]):
        score = add_points(score, reasons, 5, "explicit intended reuse signal")
    if project["statusExplicit"]:
        score = add_points(score, reasons, 5, "lifecycle state preserved")
    return min(score, 25), reasons


def classify_band(total_score: int) -> str:
    if total_score >= 80:
        return "strong"
    if total_score >= 60:
        return "emerging"
    if total_score >= 40:
        return "partial"
    return "weak"


def score_project(project: dict[str, object]) -> dict[str, object]:
    text = normalize(
        " ".join(
            [
                project["name"],
                project["path"],
                project.get("detail", ""),
                project["row"].get("Status", ""),
                project["row"].get("Paper Status", ""),
                project["row"].get("Last Touch", ""),
            ]
        )
    )
    findable, findable_reasons = score_findable(project, text)
    accessible, accessible_reasons = score_accessible(project, text)
    interoperable, interoperable_reasons = score_interoperable(project, text)
    reusable, reusable_reasons = score_reusable(project, text)
    total = findable + accessible + interoperable + reusable

    return {
        "id": project["id"],
        "name": project["name"],
        "tier": project["tierShortName"],
        "tierName": project["tierName"],
        "type": project["type"],
        "path": project["path"],
        "status": project["statusLabel"],
        "statusExplicit": project["statusExplicit"],
        "scores": {
            "findable": findable,
            "accessible": accessible,
            "interoperable": interoperable,
            "reusable": reusable,
            "total": total,
        },
        "band": classify_band(total),
        "reasons": {
            "findable": findable_reasons,
            "accessible": accessible_reasons,
            "interoperable": interoperable_reasons,
            "reusable": reusable_reasons,
        },
    }


def build_payload(source: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    scored_projects = [score_project(project) for project in source["portfolio"]]
    totals = [item["scores"]["total"] for item in scored_projects]
    band_counts = Counter(item["band"] for item in scored_projects)
    tier_scores: defaultdict[str, list[int]] = defaultdict(list)
    for item in scored_projects:
        tier_scores[item["tier"]].append(item["scores"]["total"])

    tier_means = [
        {"tier": tier, "meanScore": round(statistics.mean(values), 1), "count": len(values)}
        for tier, values in tier_scores.items()
    ]
    tier_means_sorted = sorted(tier_means, key=lambda item: (-item["meanScore"], item["tier"]))
    strong_count = sum(1 for item in scored_projects if item["scores"]["total"] >= 80)
    score_70_count = sum(1 for item in scored_projects if item["scores"]["total"] >= 70)
    score_60_count = sum(1 for item in scored_projects if item["scores"]["total"] >= 60)
    weak_count = sum(1 for item in scored_projects if item["scores"]["total"] < 40)

    score_file = {
        "project": "FAIRPortfolio",
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overview": {
            "sourcePath": source["overview"]["sourcePath"],
            "trackedProjects": len(scored_projects),
            "meanTotalScore": round(statistics.mean(totals), 1),
            "medianTotalScore": statistics.median(totals),
            "score70Count": score_70_count,
            "score70Percent": round((score_70_count / len(scored_projects)) * 100, 1),
            "score60Count": score_60_count,
            "score60Percent": round((score_60_count / len(scored_projects)) * 100, 1),
            "strongCount": strong_count,
            "strongPercent": round((strong_count / len(scored_projects)) * 100, 1),
            "weakCount": weak_count,
            "weakPercent": round((weak_count / len(scored_projects)) * 100, 1),
        },
        "scores": scored_projects,
    }

    dashboard_data = {
        "project": {
            "name": "FAIRPortfolio",
            "version": "0.1.0",
            "generatedAt": score_file["generatedAt"],
            "sourcePath": source["overview"]["sourcePath"],
            "designBasis": [
                "FAIR-inspired proxy scoring, not formal FAIR certification",
                "Per-project F/A/I/R component scoring",
                "Static GitHub Pages dashboard and E156 bundle",
            ],
        },
        "metrics": score_file["overview"],
        "bandBreakdown": [
            {"band": key.title(), "count": count}
            for key, count in sorted(band_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "bestTiers": tier_means_sorted[:6],
        "weakestTiers": sorted(tier_means, key=lambda item: (item["meanScore"], item["tier"]))[:6],
        "topProjects": sorted(scored_projects, key=lambda item: (-item["scores"]["total"], item["name"]))[:12],
        "bottomProjects": sorted(scored_projects, key=lambda item: (item["scores"]["total"], item["name"]))[:12],
        "componentMeans": {
            "findable": round(statistics.mean(item["scores"]["findable"] for item in scored_projects), 1),
            "accessible": round(statistics.mean(item["scores"]["accessible"] for item in scored_projects), 1),
            "interoperable": round(statistics.mean(item["scores"]["interoperable"] for item in scored_projects), 1),
            "reusable": round(statistics.mean(item["scores"]["reusable"] for item in scored_projects), 1),
        },
    }

    return score_file, dashboard_data


def write_outputs(score_file: dict[str, object], dashboard_data: dict[str, object]) -> None:
    FAIR_SCORES_JSON.write_text(json.dumps(score_file, indent=2), encoding="utf-8")
    DATA_JSON.write_text(json.dumps(dashboard_data, indent=2), encoding="utf-8")
    DATA_JS.write_text("window.FAIR_PORTFOLIO_DATA = " + json.dumps(dashboard_data, indent=2) + ";\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build FAIRPortfolio artifacts.")
    parser.add_argument(
        "--source",
        help="Optional path to a portfolio-data.json file. Relative paths resolve from the repository root.",
    )
    args = parser.parse_args()

    source_path = Path(args.source) if args.source else DEFAULT_SOURCE
    if not source_path.is_absolute():
        source_path = PROJECT_ROOT / source_path
    if not source_path.exists():
        raise SystemExit(f"Source data not found: {source_path}")

    source = load_payload(source_path)
    score_file, dashboard_data = build_payload(source)
    write_outputs(score_file, dashboard_data)

    metrics = dashboard_data["metrics"]
    print(
        "Built FAIRPortfolio "
        f"({metrics['trackedProjects']} projects, "
        f"mean score {metrics['meanTotalScore']}, "
        f"{metrics['score70Percent']}% at 70 or higher)."
    )


if __name__ == "__main__":
    main()
