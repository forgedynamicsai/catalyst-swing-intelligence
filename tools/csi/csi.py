#!/usr/bin/env python3
"""
Catalyst Swing Intelligence — Low-Cost Reference Implementation

Search-first crowd signal scoring. Zero required paid APIs.

Usage:
    python csi.py queries "AI data center power scarcity"
    python csi.py template --output evidence.csv
    python csi.py score evidence.csv
    python csi.py report evidence.csv --output report.md
    python csi.py demo

Crowd Signal Quality != Security Risk != Trade Decision
This tool does not make buy/sell/hold recommendations.
"""

import argparse
import csv
import io
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SOURCE_CLASSES = [
    "primary_filing",
    "earnings_transcript",
    "company_ir",
    "major_news",
    "trade_publication",
    "investing_forum",
    "social_media",
    "prediction_market",
    "pundit",
    "whale_positioning",
    "copy_trading",
    "market_data",
    "unknown",
]

SOURCE_GROUPS = {
    "primary_factual": {"primary_filing", "earnings_transcript", "company_ir"},
    "crowd_social_forum": {"investing_forum", "social_media"},
    "news": {"major_news", "trade_publication"},
    "prediction_market_positioning": {
        "prediction_market",
        "whale_positioning",
        "copy_trading",
        "market_data",
    },
}

QUERY_TEMPLATES = {
    "major_news": [
        '"{theme}" Reuters',
        '"{theme}" Bloomberg',
        '"{theme}" site:wsj.com OR site:ft.com',
    ],
    "filings_transcripts": [
        '"{theme}" earnings call transcript',
        '"{theme}" SEC filing 10-K OR 10-Q OR 8-K',
    ],
    "prediction_markets": [
        '"{theme}" Polymarket',
        '"{theme}" Kalshi',
        '"{theme}" Metaculus',
    ],
    "investing_forums": [
        '"{theme}" Reddit r/investing OR r/stocks OR r/wallstreetbets',
        '"{theme}" Seeking Alpha',
        '"{theme}" StockTwits',
    ],
    "social_media": [
        '"{theme}" Twitter OR X fintwit',
        '"{theme}" LinkedIn analyst',
    ],
    "pundits": [
        '"{theme}" Jim Cramer',
        '"{theme}" analyst upgrade downgrade',
    ],
    "whale_positioning": [
        '"{theme}" 13F institutional positioning',
        '"{theme}" options unusual activity',
    ],
    "copy_trading": [
        '"{theme}" retail flow copy trading',
        '"{theme}" eToro popular investor',
    ],
    "market_data": [
        '"{theme}" short interest',
        '"{theme}" price chart volume analysis',
    ],
}

EVIDENCE_COLUMNS = [
    "claim",
    "source_name",
    "source_url",
    "source_class",
    "source_date",
    "source_type",
    "independence_rating",
    "evidence_quality",
    "specificity",
    "catalyst_alignment",
    "dissent_quality",
    "time_signal",
    "is_duplicate",
    "notes",
]

NUMERIC_COLS = {
    "independence_rating": (0, 20),
    "evidence_quality": (0, 20),
    "specificity": (0, 20),
    "catalyst_alignment": (0, 10),
    "dissent_quality": (0, 5),
    "time_signal": (0, 10),
}

DISCLAIMER = (
    "This score measures Crowd Signal Quality only. "
    "It is NOT a buy/sell/hold score, expected return, security risk rating, "
    "or financial advice."
)

# ---------------------------------------------------------------------------
# Evidence loading
# ---------------------------------------------------------------------------


def load_evidence(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append(row)
    return rows


def _parse_bool(val: str) -> bool:
    return str(val).strip().lower() in ("true", "1", "yes")


def _parse_int(val: str, col: str) -> int:
    try:
        v = int(str(val).strip())
        lo, hi = NUMERIC_COLS[col]
        return max(lo, min(hi, v))
    except (ValueError, TypeError):
        return 0


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# ---------------------------------------------------------------------------
# Dedupe / echo-chamber check
# ---------------------------------------------------------------------------


def dedupe_check(rows: list[dict]) -> dict:
    total = len(rows)
    explicit = sum(1 for r in rows if _parse_bool(r.get("is_duplicate", "false")))

    seen_urls: set[str] = set()
    seen_claims: set[str] = set()
    inferred = 0
    for r in rows:
        url = r.get("source_url", "").strip()
        claim = r.get("claim", "").strip().lower()
        if url and url in seen_urls:
            inferred += 1
        elif claim and claim in seen_claims:
            inferred += 1
        else:
            if url:
                seen_urls.add(url)
            if claim:
                seen_claims.add(claim)

    dup_count = max(explicit, inferred)
    dup_ratio = dup_count / total if total > 0 else 0.0
    echo_chamber = dup_ratio >= 0.5

    return {
        "duplicate_count": dup_count,
        "duplicate_ratio": round(dup_ratio, 2),
        "possible_echo_chamber": echo_chamber,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def _volume_score(non_dup_count: int) -> int:
    if non_dup_count == 0:
        return 0
    if non_dup_count == 1:
        return 4
    if non_dup_count == 2:
        return 8
    if non_dup_count <= 4:
        return 11
    if non_dup_count <= 7:
        return 13
    return 15


def _penalty_from_notes(rows: list[dict], markers: list[str], max_penalty: int) -> int:
    all_notes = " ".join(r.get("notes", "") for r in rows).lower()
    for marker in markers:
        if marker in all_notes:
            return max_penalty
    return 0


def score_evidence(rows: list[dict]) -> dict:
    if not rows:
        return {
            "score": 0,
            "confidence": "no-evidence",
            "source_coverage_grade": "F",
            "components": {},
            "penalties": {},
            "trajectory": "unknown",
            "dedupe": {"duplicate_count": 0, "duplicate_ratio": 0.0, "possible_echo_chamber": False},
            "disclaimer": DISCLAIMER,
        }

    non_dup_rows = [r for r in rows if not _parse_bool(r.get("is_duplicate", "false"))]

    # Base components
    volume = _volume_score(len(non_dup_rows))
    independence = min(20, round(_avg([_parse_int(r.get("independence_rating", 0), "independence_rating") for r in non_dup_rows])))
    specificity = min(20, round(_avg([_parse_int(r.get("specificity", 0), "specificity") for r in non_dup_rows])))
    evidence_quality = min(20, round(_avg([_parse_int(r.get("evidence_quality", 0), "evidence_quality") for r in non_dup_rows])))
    time_accel = min(10, round(_avg([_parse_int(r.get("time_signal", 0), "time_signal") for r in non_dup_rows])))
    catalyst_align = min(10, round(_avg([_parse_int(r.get("catalyst_alignment", 0), "catalyst_alignment") for r in non_dup_rows])))
    dissent = min(5, round(_avg([_parse_int(r.get("dissent_quality", 0), "dissent_quality") for r in non_dup_rows])))

    base = volume + independence + specificity + evidence_quality + time_accel + catalyst_align + dissent

    # Penalties from notes
    meme_hype = _penalty_from_notes(
        rows, ["meme", "yolo", "rocket", "guaranteed", "moon", "can't lose", "cant lose"], 15
    )
    crowding = _penalty_from_notes(
        rows, ["crowded", "consensus", "everyone knows", "mainstream", "saturated"], 15
    )
    price_moved = _penalty_from_notes(
        rows, ["already moved", "priced in", "gap up", "extended", "already ran"], 20
    )
    loose_basket = _penalty_from_notes(
        rows, ["basket", "loose", "unclear ticker", "weak expression"], 10
    )

    # Single-source penalty
    source_names = [r.get("source_name", "").strip() for r in non_dup_rows if r.get("source_name", "").strip()]
    source_classes = [r.get("source_class", "").strip() for r in non_dup_rows if r.get("source_class", "").strip()]
    single_source = 0
    if len(set(source_names)) <= 1 or len(set(source_classes)) <= 1:
        single_source = 20

    # Duplicate penalty
    dup_ratio = dedupe_check(rows)["duplicate_ratio"]
    dup_penalty = min(10, round(dup_ratio * 10))

    # Unknown source penalty
    unknown_ratio = sum(1 for r in rows if r.get("source_class", "").strip() == "unknown") / len(rows)
    unknown_penalty = min(10, round(unknown_ratio * 10))

    total_penalties = meme_hype + crowding + price_moved + loose_basket + single_source + dup_penalty + unknown_penalty
    final_score = max(0, min(100, base - total_penalties))

    # Source coverage grade
    grade = _source_coverage_grade(rows)

    # Confidence label
    if grade in ("D", "F"):
        confidence = "no-full-confidence / source-limited"
    elif grade == "C":
        confidence = "provisional / source-limited"
    else:
        confidence = "standard"

    # Trajectory
    trajectory = _classify_trajectory(rows, non_dup_rows, time_accel, crowding, price_moved)

    dedupe = dedupe_check(rows)

    return {
        "score": final_score,
        "confidence": confidence,
        "source_coverage_grade": grade,
        "components": {
            "volume": volume,
            "source_independence": independence,
            "specificity": specificity,
            "evidence_quality": evidence_quality,
            "time_acceleration": time_accel,
            "catalyst_alignment": catalyst_align,
            "dissent_quality": dissent,
            "base_total": base,
        },
        "penalties": {
            "meme_hype": -meme_hype if meme_hype else 0,
            "crowding": -crowding if crowding else 0,
            "price_moved": -price_moved if price_moved else 0,
            "loose_ticker_basket": -loose_basket if loose_basket else 0,
            "single_source": -single_source if single_source else 0,
            "duplicate": -dup_penalty if dup_penalty else 0,
            "unknown_source": -unknown_penalty if unknown_penalty else 0,
        },
        "trajectory": trajectory,
        "dedupe": dedupe,
        "disclaimer": DISCLAIMER,
    }


def _source_coverage_grade(rows: list[dict]) -> str:
    if not rows:
        return "F"

    present: set[str] = set()
    has_dissent = False

    for r in rows:
        sc = r.get("source_class", "").strip()
        for group, members in SOURCE_GROUPS.items():
            if sc in members:
                present.add(group)
        if _parse_int(r.get("dissent_quality", 0), "dissent_quality") > 0:
            has_dissent = True

    if not present:
        return "F"

    has_primary = "primary_factual" in present
    has_crowd = "crowd_social_forum" in present
    has_news = "news" in present
    has_pred = "prediction_market_positioning" in present

    if has_primary and has_crowd and (has_pred or has_news) and has_dissent:
        return "A"
    if has_primary and has_crowd and (has_news or has_pred):
        return "B"
    if has_crowd and has_news:
        return "C"
    if len(present) == 1:
        return "D"
    return "C"


def _classify_trajectory(
    rows: list[dict],
    non_dup_rows: list[dict],
    time_accel: float,
    crowding_penalty: int,
    price_moved_penalty: int,
) -> str:
    if not rows:
        return "unknown"

    dated = [r for r in rows if r.get("source_date", "").strip()]
    if len(dated) < 2:
        return "unknown"

    all_notes = " ".join(r.get("notes", "") for r in rows).lower()

    if any(w in all_notes for w in ["fading", "stale", "old signal", "no new sources", "repeated"]):
        return "fading"

    if crowding_penalty > 0 or any(
        w in all_notes for w in ["saturated", "mainstream", "everyone"]
    ):
        return "saturated"

    source_classes = [r.get("source_class", "").strip() for r in non_dup_rows]
    has_major_news = "major_news" in source_classes or "trade_publication" in source_classes
    has_social = "social_media" in source_classes or "investing_forum" in source_classes

    if has_major_news and has_social:
        return "mainstreaming"

    source_names = set(r.get("source_name", "").strip() for r in non_dup_rows if r.get("source_name", "").strip())
    if time_accel >= 7 and len(source_names) >= 3:
        return "accelerating"

    count = len(non_dup_rows)
    avg_specificity = _avg([_parse_int(r.get("specificity", 0), "specificity") for r in non_dup_rows])
    avg_eq = _avg([_parse_int(r.get("evidence_quality", 0), "evidence_quality") for r in non_dup_rows])

    if count <= 3 and (avg_specificity >= 12 or avg_eq >= 12):
        return "emerging"

    if count >= 2:
        return "accelerating"

    return "emerging"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_queries(theme: str) -> str:
    lines = [f"Search queries for theme: {theme}\n"]
    for category, templates in QUERY_TEMPLATES.items():
        lines.append(f"\n## {category.replace('_', ' ').title()}")
        for t in templates:
            lines.append(f'  {t.format(theme=theme)}')
    lines.append(
        "\n\nNote: These queries are for manual or agent-driven search. "
        "No searches are executed. Cost: $0.\n\n"
        "After searching, enter findings into evidence.csv with:\n"
        "  python tools/csi/csi.py template --output evidence.csv"
    )
    return "\n".join(lines)


def cmd_template(output_path: str) -> str:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EVIDENCE_COLUMNS)
        writer.writeheader()
        writer.writerow({col: "" for col in EVIDENCE_COLUMNS})
    return f"Template written to {output_path}\nColumns: {', '.join(EVIDENCE_COLUMNS)}"


def cmd_score(evidence_path: str) -> str:
    rows = load_evidence(evidence_path)
    result = score_evidence(rows)

    lines = [
        f"Crowd Signal Quality Score: {result['score']}/100",
        f"Confidence: {result['confidence']}",
        f"Source Coverage Grade: {result['source_coverage_grade']}",
        f"Signal Trajectory: {result['trajectory']}",
        f"Echo-Chamber Risk: {result['dedupe']['possible_echo_chamber']}",
        f"Duplicate Count: {result['dedupe']['duplicate_count']} / {len(rows)}",
        "",
        "Score Breakdown:",
    ]
    for k, v in result["components"].items():
        lines.append(f"  {k}: {v}")

    lines.append("\nPenalties Applied:")
    for k, v in result["penalties"].items():
        if v != 0:
            lines.append(f"  {k}: {v}")
        else:
            lines.append(f"  {k}: none")

    lines.append(f"\n{result['disclaimer']}")
    return "\n".join(lines)


def cmd_report(evidence_path: str, output_path: str | None, theme: str = "") -> str:
    rows = load_evidence(evidence_path)
    result = score_evidence(rows)

    theme_label = theme if theme else Path(evidence_path).stem
    md = _build_report_markdown(theme_label, rows, result)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)
        return f"Report written to {output_path}"
    return md


def _build_report_markdown(theme: str, rows: list[dict], result: dict) -> str:
    lines = [
        f"# Crowd Signal Report: {theme}",
        "",
        "## Executive Summary",
        "",
        f"- **Crowd Signal Quality Score:** {result['score']}/100",
        f"- **Confidence:** {result['confidence']}",
        f"- **Source Coverage Grade:** {result['source_coverage_grade']}",
        f"- **Signal Trajectory:** {result['trajectory']}",
        f"- **Echo-Chamber Risk:** {result['dedupe']['possible_echo_chamber']}",
        f"- **Duplicates:** {result['dedupe']['duplicate_count']} / {len(rows)}",
        "- **Not a buy/sell/hold recommendation.**",
        "",
        "---",
        "",
        "## Score Breakdown",
        "",
        "| Component | Score | Max |",
        "|---|---:|---:|",
    ]

    max_map = {
        "volume": 15,
        "source_independence": 20,
        "specificity": 20,
        "evidence_quality": 20,
        "time_acceleration": 10,
        "catalyst_alignment": 10,
        "dissent_quality": 5,
        "base_total": 100,
    }
    for k, v in result["components"].items():
        lines.append(f"| {k.replace('_', ' ').title()} | {v} | {max_map.get(k, '')} |")

    lines += [
        "",
        "---",
        "",
        "## Penalties Applied",
        "",
        "| Penalty | Deduction | Why |",
        "|---|---:|---|",
    ]

    penalty_why = {
        "meme_hype": "hype language detected in notes",
        "crowding": "crowding/consensus language detected",
        "price_moved": "price-moved language detected",
        "loose_ticker_basket": "loose basket language detected",
        "single_source": "all evidence from one source class or name",
        "duplicate": "duplicate row ratio",
        "unknown_source": "unknown source class ratio",
    }
    any_penalty = False
    for k, v in result["penalties"].items():
        if v != 0:
            lines.append(f"| {k.replace('_', ' ').title()} | {v} | {penalty_why.get(k, '')} |")
            any_penalty = True
    if not any_penalty:
        lines.append("| None | 0 | — |")

    lines += [
        "",
        "---",
        "",
        "## Source Coverage",
        "",
        "| Source Group | Present? | Evidence Count |",
        "|---|---:|---:|",
    ]

    for group, members in SOURCE_GROUPS.items():
        count = sum(1 for r in rows if r.get("source_class", "").strip() in members)
        present = "Yes" if count > 0 else "No"
        lines.append(f"| {group.replace('_', ' ').title()} | {present} | {count} |")

    dissent_count = sum(
        1 for r in rows if _parse_int(r.get("dissent_quality", 0), "dissent_quality") > 0
    )
    lines.append(f"| Dissent (quality > 0) | {'Yes' if dissent_count else 'No'} | {dissent_count} |")

    lines += [
        "",
        "---",
        "",
        "## Evidence Table",
        "",
        "| Claim | Source | Class | Date | Evidence Quality | Notes |",
        "|---|---|---|---|---:|---|",
    ]

    for r in rows:
        claim = r.get("claim", "")[:60].replace("|", "\\|")
        source = r.get("source_name", "")[:30].replace("|", "\\|")
        sc = r.get("source_class", "")
        date = r.get("source_date", "")
        eq = r.get("evidence_quality", "")
        notes = r.get("notes", "")[:40].replace("|", "\\|")
        lines.append(f"| {claim} | {source} | {sc} | {date} | {eq} | {notes} |")

    gaps = _identify_gaps(rows)
    lines += [
        "",
        "---",
        "",
        "## Gaps and Unknowns",
        "",
    ]
    lines.extend(f"- {g}" for g in gaps)

    lines += [
        "",
        "---",
        "",
        "## Interpretation",
        "",
        result["disclaimer"],
        "",
        "> Signal trajectory describes crowd narrative lifecycle only.",
        "> It does not forecast price direction, expected return, or fair value.",
    ]

    return "\n".join(lines)


def _identify_gaps(rows: list[dict]) -> list[str]:
    gaps = []
    classes_present = {r.get("source_class", "").strip() for r in rows}
    for group, members in SOURCE_GROUPS.items():
        if not classes_present.intersection(members):
            gaps.append(f"No {group.replace('_', ' ')} sources present.")
    if not any(_parse_int(r.get("dissent_quality", 0), "dissent_quality") > 0 for r in rows):
        gaps.append("No dissent evidence collected.")
    unknown_count = sum(1 for r in rows if r.get("source_class", "").strip() == "unknown")
    if unknown_count:
        gaps.append(f"{unknown_count} row(s) have unknown source class — reclassify if possible.")
    if not gaps:
        gaps.append("No major source gaps identified.")
    return gaps


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

DEMO_CSV = """claim,source_name,source_url,source_class,source_date,source_type,independence_rating,evidence_quality,specificity,catalyst_alignment,dissent_quality,time_signal,is_duplicate,notes
"Power demand from AI data centers will exceed grid capacity by 2026 in key markets","TechPub Research","https://example.com/techpub1","trade_publication","2025-11-01","article",15,16,15,8,0,8,false,"analyst report; strong mechanism"
"Three hyperscalers cited power scarcity on Q3 earnings calls","EarningsTracker","https://example.com/et1","earnings_transcript","2025-10-20","transcript",18,18,17,9,3,9,false,"primary source; named catalyst"
"AI power demand narrative gaining traction on investing forums","ForumAgg","https://example.com/forum1","investing_forum","2025-11-10","forum",8,6,10,6,2,7,false,"growing thread count"
"Crowd signal quality is provisional — grid constraints are regional not universal","BearAnalyst","https://example.com/bear1","trade_publication","2025-11-05","article",14,13,12,5,4,6,false,"credible dissent; regional caveat"
"Power contract announcements accelerating per SEC filings","FilingScanner","https://example.com/sec1","primary_filing","2025-10-15","filing",17,17,16,9,0,8,false,"cross-checked 3 filings"
"Retail chatter on social media about AI power plays","SocialAgg","https://example.com/social1","social_media","2025-11-12","social",5,4,6,4,0,9,false,"volume rising; low evidence quality"
"""


def cmd_demo() -> str:
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write(DEMO_CSV)
        tmp_path = f.name

    try:
        rows = load_evidence(tmp_path)
        result = score_evidence(rows)
        report = _build_report_markdown("AI Data Center Power Scarcity (Demo)", rows, result)
    finally:
        os.unlink(tmp_path)

    return report + "\n\n---\n\n> Demo uses fictional data. Not financial advice."


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Catalyst Swing Intelligence — low-cost crowd signal scoring CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_q = sub.add_parser("queries", help="Generate source-targeted search queries")
    p_q.add_argument("theme", help="Market theme to generate queries for")

    p_t = sub.add_parser("template", help="Create blank evidence CSV template")
    p_t.add_argument("--output", default="evidence.csv", help="Output path (default: evidence.csv)")

    p_s = sub.add_parser("score", help="Score an evidence CSV")
    p_s.add_argument("evidence", help="Path to evidence CSV file")

    p_r = sub.add_parser("report", help="Generate markdown crowd signal report")
    p_r.add_argument("evidence", help="Path to evidence CSV file")
    p_r.add_argument("--output", default=None, help="Output path (prints to stdout if omitted)")
    p_r.add_argument("--theme", default="", help="Theme label for report title")

    sub.add_parser("demo", help="Run built-in demo with sample evidence")

    # Memory flywheel commands
    p_obs = sub.add_parser("observe", help="Score evidence and save as an observation")
    p_obs.add_argument("evidence", help="Path to evidence CSV file")
    p_obs.add_argument("--theme", required=True, help="Market theme for this signal")
    p_obs.add_argument("--notes", default="", help="Optional notes")
    p_obs.add_argument("--data-dir", default="data/csi", help="Observations data directory")
    p_obs.add_argument("--reports-dir", default="reports/csi", help="Reports output directory")

    p_ls = sub.add_parser("list", help="List stored observations")
    p_ls.add_argument("--month", default=None, help="Filter by month (YYYY-MM)")
    p_ls.add_argument("--data-dir", default="data/csi", help="Observations data directory")

    p_out = sub.add_parser("outcome", help="Attach outcome review to an observation")
    p_out.add_argument("signal_id", help="Signal ID to review")
    p_out.add_argument("--event-confirmed", default="unknown", help="true|false|unknown")
    p_out.add_argument("--narrative-mainstreamed", default="unknown", help="true|false|unknown")
    p_out.add_argument("--trajectory-correct", default="unknown", help="true|false|unknown")
    p_out.add_argument("--catalyst-occurred", default="unknown", help="true|false|unknown")
    p_out.add_argument("--transmission-confirmed", default="unknown", help="yes|partial|no|unknown")
    p_out.add_argument("--usefulness", default="unknown", help="useful|mixed|not_useful|unknown")
    p_out.add_argument("--failure-mode", default="none",
                       help="none|single_source|hype|priced_in|wrong_transmission|no_catalyst|trajectory_wrong|other")
    p_out.add_argument("--notes", default="", help="Optional notes")
    p_out.add_argument("--data-dir", default="data/csi", help="Data directory")

    p_mr = sub.add_parser("monthly-review", help="Generate monthly effectiveness review")
    p_mr.add_argument("--month", required=True, help="Month to review (YYYY-MM)")
    p_mr.add_argument("--output", default=None, help="Output path")
    p_mr.add_argument("--data-dir", default="data/csi", help="Data directory")

    p_pb = sub.add_parser("playbook", help="Generate crowd signal playbook from accumulated data")
    p_pb.add_argument("--output", default="playbooks/crowd-signal-playbook.md", help="Output path")
    p_pb.add_argument("--data-dir", default="data/csi", help="Data directory")

    # v0.5 operability commands
    p_val = sub.add_parser("validate", help="Validate evidence CSV schema and values")
    p_val.add_argument("evidence", help="Path to evidence CSV file")
    p_val.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    p_imd = sub.add_parser("import-md", help="Import markdown evidence table to CSV")
    p_imd.add_argument("markdown", help="Path to markdown file containing evidence table")
    p_imd.add_argument("--output", default="evidence.csv", help="Output CSV path")
    p_imd.add_argument("--append", action="store_true", help="Append to existing CSV")

    p_wiz = sub.add_parser("wizard", help="Guided evidence-to-memory workflow")
    p_wiz.add_argument("--theme", default="", help="Market theme (skips theme prompt)")
    p_wiz.add_argument("--evidence", default="", help="Path to existing evidence CSV")
    p_wiz.add_argument("--dry-run", action="store_true",
                       help="Print planned workflow without interactive prompts")
    p_wiz.add_argument("--data-dir", default="data/csi", help="Observations data directory")
    p_wiz.add_argument("--reports-dir", default="reports/csi", help="Reports directory")

    args = parser.parse_args()

    if args.command == "queries":
        print(cmd_queries(args.theme))
    elif args.command == "template":
        print(cmd_template(args.output))
    elif args.command == "score":
        print(cmd_score(args.evidence))
    elif args.command == "report":
        print(cmd_report(args.evidence, args.output, args.theme))
    elif args.command == "demo":
        print(cmd_demo())
    elif args.command == "observe":
        import memory as _mem
        print(_mem.cmd_observe(
            args.evidence, args.theme, args.notes,
            args.data_dir, args.reports_dir,
        ))
    elif args.command == "list":
        import memory as _mem
        print(_mem.cmd_list(args.month, args.data_dir))
    elif args.command == "outcome":
        import memory as _mem
        print(_mem.cmd_outcome(
            args.signal_id,
            event_confirmed=args.event_confirmed,
            narrative_mainstreamed=args.narrative_mainstreamed,
            trajectory_correct=args.trajectory_correct,
            catalyst_occurred=args.catalyst_occurred,
            transmission_confirmed=args.transmission_confirmed,
            usefulness=args.usefulness,
            failure_mode=args.failure_mode,
            notes=args.notes,
            data_dir=args.data_dir,
        ))
    elif args.command == "monthly-review":
        import memory as _mem
        print(_mem.cmd_monthly_review(args.month, args.data_dir, args.output))
    elif args.command == "playbook":
        import memory as _mem
        print(_mem.cmd_playbook(args.data_dir, args.output))
    elif args.command == "validate":
        import validation as _val
        output, code = _val.cmd_validate(args.evidence, args.strict)
        print(output)
        sys.exit(code)
    elif args.command == "import-md":
        import importer as _imp
        output, code = _imp.import_md(args.markdown, args.output, args.append)
        print(output)
        sys.exit(code)
    elif args.command == "wizard":
        import wizard as _wiz
        _wiz.run_wizard(
            theme=args.theme,
            evidence_path=args.evidence,
            dry_run=args.dry_run,
            data_dir=args.data_dir,
            reports_dir=args.reports_dir,
        )


if __name__ == "__main__":
    main()
