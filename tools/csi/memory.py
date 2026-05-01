"""
Memory flywheel for crowd signal effectiveness tracking.

Score signal → Save observation → Track outcome → Monthly review →
Suggested playbook updates → Better future crowd-signal assessment.

This system learns which crowd-signal patterns were useful.
It does not learn which stocks to buy.

Crowd Signal Playbook ≠ Investment Playbook
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Non-advisory boundary — enforced throughout
# ---------------------------------------------------------------------------

NON_ADVISORY_BOUNDARY = (
    "This system evaluates crowd-signal usefulness. "
    "It does not recommend purchases, investments, trades, "
    "position sizing, or buy/sell/hold actions."
)

PLAYBOOK_BOUNDARY = (
    "Crowd Signal Playbook ≠ Investment Playbook\n\n"
    "This playbook is for improving crowd-signal assessment only. "
    "It does not recommend purchases, investments, trades, "
    "position sizing, or buy/sell/hold actions for any security."
)

# ---------------------------------------------------------------------------
# Signal classification (replaces tradeable/watchlist/reject)
# ---------------------------------------------------------------------------

CLASSIFICATIONS = ("analysis-ready", "monitor", "reject")

CLASSIFICATION_DEFINITIONS = {
    "analysis-ready": (
        "The crowd signal is sufficiently sourced and coherent to justify separate "
        "thesis, valuation, entry, and risk review. "
        "Not a buy/sell/hold recommendation."
    ),
    "monitor": (
        "The crowd signal is interesting but incomplete, source-limited, "
        "too early, too crowded, or missing key evidence."
    ),
    "reject": (
        "The crowd signal lacks sufficient independent evidence, specificity, "
        "mechanism, or source coverage, or is dominated by hype/echo-chamber risk."
    ),
}


def classify_signal(score_result: dict) -> str:
    """Deterministic signal classification based on score + coverage + confidence."""
    score = score_result.get("score", 0)
    grade = score_result.get("source_coverage_grade", "F")
    confidence = score_result.get("confidence", "")

    if "no-evidence" in confidence or grade == "F":
        return "reject"
    if grade == "D":
        return "reject"
    if score < 35:
        return "reject"
    if score >= 55 and grade in ("A", "B") and confidence == "standard":
        return "analysis-ready"
    return "monitor"


# ---------------------------------------------------------------------------
# ID and slug helpers
# ---------------------------------------------------------------------------


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80]


def make_signal_id(theme: str, existing_ids: set[str], date_str: str | None = None) -> str:
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base = f"{date_str}-{_slugify(theme)}"
    if base not in existing_ids:
        return base
    n = 2
    while f"{base}-{n}" in existing_ids:
        n += 1
    return f"{base}-{n}"


# ---------------------------------------------------------------------------
# JSONL helpers
# ---------------------------------------------------------------------------


def _ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def load_jsonl(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    records = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def append_jsonl(path: str, record: dict) -> None:
    _ensure_dir(str(Path(path).parent))
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------------------
# Observation helpers
# ---------------------------------------------------------------------------


def load_all_observations(data_dir: str) -> list[dict]:
    return load_jsonl(os.path.join(data_dir, "observations.jsonl"))


def load_all_outcomes(data_dir: str) -> list[dict]:
    return load_jsonl(os.path.join(data_dir, "outcomes.jsonl"))


def _outcomes_by_id(outcomes: list[dict]) -> dict[str, list[dict]]:
    mapping: dict[str, list[dict]] = {}
    for o in outcomes:
        sid = o.get("signal_id", "")
        mapping.setdefault(sid, []).append(o)
    return mapping


# ---------------------------------------------------------------------------
# Command: observe
# ---------------------------------------------------------------------------


def cmd_observe(
    evidence_path: str,
    theme: str,
    notes: str = "",
    data_dir: str = "data/csi",
    reports_dir: str = "reports/csi",
) -> str:
    # Import scoring from sibling module — lazy to avoid circular import at module level
    import csi as _csi  # noqa: F401

    rows = _csi.load_evidence(evidence_path)
    score_result = _csi.score_evidence(rows)
    classification = classify_signal(score_result)

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    existing = load_all_observations(data_dir)
    existing_ids = {o["signal_id"] for o in existing}
    signal_id = make_signal_id(theme, existing_ids, date_str)

    report_filename = f"{signal_id}.md"
    report_path = os.path.join(reports_dir, report_filename)
    _ensure_dir(reports_dir)

    report_md = _csi._build_report_markdown(theme, rows, score_result)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    source_classes = list({r.get("source_class", "").strip() for r in rows if r.get("source_class", "").strip()})
    source_group_coverage = {
        group: any(r.get("source_class", "").strip() in members for r in rows)
        for group, members in _csi.SOURCE_GROUPS.items()
    }
    source_group_coverage["dissent"] = any(
        _csi._parse_int(r.get("dissent_quality", 0), "dissent_quality") > 0 for r in rows
    )

    observation = {
        "signal_id": signal_id,
        "created_at": ts,
        "theme": theme,
        "crowd_signal_quality_score": score_result["score"],
        "confidence": score_result["confidence"],
        "source_coverage_grade": score_result["source_coverage_grade"],
        "signal_trajectory": score_result["trajectory"],
        "echo_chamber_risk": score_result["dedupe"]["possible_echo_chamber"],
        "source_classes": source_classes,
        "source_group_coverage": source_group_coverage,
        "classification": classification,
        "report_path": report_path,
        "evidence_path": evidence_path,
        "notes": notes,
    }

    obs_path = os.path.join(data_dir, "observations.jsonl")
    append_jsonl(obs_path, observation)

    lines = [
        "Observation saved.",
        f"Signal ID:      {signal_id}",
        f"Score:          {score_result['score']}/100",
        f"Coverage:       {score_result['source_coverage_grade']}",
        f"Confidence:     {score_result['confidence']}",
        f"Trajectory:     {score_result['trajectory']}",
        f"Classification: {classification}",
        f"Report:         {report_path}",
        "",
        f"Reminder: {classification} is not a buy/sell/hold recommendation.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Command: list
# ---------------------------------------------------------------------------


def cmd_list(month: str | None = None, data_dir: str = "data/csi") -> str:
    observations = load_all_observations(data_dir)
    outcomes = load_all_outcomes(data_dir)
    reviewed_ids = {o["signal_id"] for o in outcomes}

    if month:
        observations = [
            o for o in observations
            if o.get("created_at", "").startswith(month)
        ]

    if not observations:
        return "No observations found." + (f" (month: {month})" if month else "")

    header = f"{'Signal ID':<50} {'Date':<12} {'Score':>5} {'Cov':>3} {'Traj':<15} {'Class':<16} {'Outcome':<10}"
    sep = "-" * len(header)
    lines = [header, sep]
    for o in observations:
        sid = o.get("signal_id", "")[:48]
        date = o.get("created_at", "")[:10]
        score = o.get("crowd_signal_quality_score", "?")
        grade = o.get("source_coverage_grade", "?")
        traj = o.get("signal_trajectory", "?")[:14]
        cls = o.get("classification", "?")[:15]
        outcome_status = "reviewed" if sid in reviewed_ids else "unreviewed"
        lines.append(f"{sid:<50} {date:<12} {score:>5} {grade:>3} {traj:<15} {cls:<16} {outcome_status}")

    lines.append(sep)
    lines.append(f"Total: {len(observations)} signal(s)")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Command: outcome
# ---------------------------------------------------------------------------

VALID_TRANSMISSION = {"yes", "partial", "no", "unknown"}
VALID_USEFULNESS = {"useful", "mixed", "not_useful", "unknown"}
VALID_FAILURE_MODES = {
    "none", "single_source", "hype", "priced_in",
    "wrong_transmission", "no_catalyst", "trajectory_wrong", "other",
}


def cmd_outcome(
    signal_id: str,
    event_confirmed: str = "unknown",
    narrative_mainstreamed: str = "unknown",
    trajectory_correct: str = "unknown",
    catalyst_occurred: str = "unknown",
    transmission_confirmed: str = "unknown",
    usefulness: str = "unknown",
    failure_mode: str = "none",
    notes: str = "",
    data_dir: str = "data/csi",
) -> str:
    observations = load_all_observations(data_dir)
    known_ids = {o["signal_id"] for o in observations}

    if signal_id not in known_ids:
        raise SystemExit(
            f"Error: signal_id '{signal_id}' not found in {data_dir}/observations.jsonl\n"
            f"Run: python csi.py list  to see available signal IDs."
        )

    if transmission_confirmed not in VALID_TRANSMISSION:
        transmission_confirmed = "unknown"
    if usefulness not in VALID_USEFULNESS:
        usefulness = "unknown"
    if failure_mode not in VALID_FAILURE_MODES:
        failure_mode = "other"

    outcomes = load_all_outcomes(data_dir)
    existing = [o for o in outcomes if o.get("signal_id") == signal_id]
    warning = ""
    if existing:
        warning = f"Warning: outcome already exists for {signal_id}. Appending additional outcome.\n"

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    outcome = {
        "signal_id": signal_id,
        "reviewed_at": ts,
        "event_confirmed": event_confirmed,
        "narrative_mainstreamed": narrative_mainstreamed,
        "trajectory_correct": trajectory_correct,
        "catalyst_occurred": catalyst_occurred,
        "transmission_confirmed": transmission_confirmed,
        "signal_usefulness": usefulness,
        "failure_mode": failure_mode,
        "notes": notes,
    }

    out_path = os.path.join(data_dir, "outcomes.jsonl")
    append_jsonl(out_path, outcome)

    return (
        f"{warning}"
        f"Outcome saved for: {signal_id}\n"
        f"Usefulness:        {usefulness}\n"
        f"Failure mode:      {failure_mode}\n"
        f"Transmission:      {transmission_confirmed}\n"
        f"Reviewed at:       {ts}\n\n"
        f"{NON_ADVISORY_BOUNDARY}"
    )


# ---------------------------------------------------------------------------
# Command: monthly-review
# ---------------------------------------------------------------------------


def cmd_monthly_review(
    month: str,
    data_dir: str = "data/csi",
    output_path: str | None = None,
) -> str:
    if not output_path:
        output_path = f"reviews/csi/{month}-monthly-review.md"

    all_obs = load_all_observations(data_dir)
    all_out = load_all_outcomes(data_dir)

    month_obs = [o for o in all_obs if o.get("created_at", "").startswith(month)]
    by_id = _outcomes_by_id(all_out)

    md = _build_monthly_review_md(month, month_obs, by_id)

    _ensure_dir(str(Path(output_path).parent))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

    return f"Monthly review written to: {output_path}"


def _bool_str(val: str) -> bool | None:
    if str(val).lower() == "true":
        return True
    if str(val).lower() == "false":
        return False
    return None


def _build_monthly_review_md(
    month: str,
    month_obs: list[dict],
    by_id: dict[str, list[dict]],
) -> str:
    signals_scored = len(month_obs)
    reviewed_obs = [o for o in month_obs if o["signal_id"] in by_id]
    unreviewed_obs = [o for o in month_obs if o["signal_id"] not in by_id]
    signals_reviewed = len(reviewed_obs)

    # Flatten outcomes for reviewed signals
    flat_outcomes = []
    for o in reviewed_obs:
        outs = by_id.get(o["signal_id"], [])
        if outs:
            flat_outcomes.append((o, outs[-1]))  # use latest outcome

    useful = sum(1 for _, out in flat_outcomes if out.get("signal_usefulness") == "useful")
    mixed = sum(1 for _, out in flat_outcomes if out.get("signal_usefulness") == "mixed")
    not_useful = sum(1 for _, out in flat_outcomes if out.get("signal_usefulness") == "not_useful")
    unknown_count = signals_reviewed - useful - mixed - not_useful

    avg_score = (
        round(sum(o.get("crowd_signal_quality_score", 0) for o in month_obs) / signals_scored, 1)
        if signals_scored else 0
    )

    lines = [
        f"# Monthly Crowd Signal Effectiveness Review — {month}",
        "",
        "## Summary",
        "",
        f"- Signals scored:          {signals_scored}",
        f"- Signals reviewed:        {signals_reviewed}",
        f"- Useful:                  {useful}",
        f"- Mixed:                   {mixed}",
        f"- Not useful:              {not_useful}",
        f"- Unreviewed:              {len(unreviewed_obs)}",
        f"- Average Score:           {avg_score}/100",
        "",
        "---",
        "",
    ]

    # What worked / failed
    what_worked = []
    what_failed = []
    for obs, out in flat_outcomes:
        usefulness = out.get("signal_usefulness", "unknown")
        if usefulness == "useful":
            what_worked.append(
                f"- **{obs['theme']}** (score {obs['crowd_signal_quality_score']}, "
                f"grade {obs['source_coverage_grade']}, "
                f"trajectory {obs['signal_trajectory']})"
            )
        elif usefulness in ("not_useful", "mixed"):
            fm = out.get("failure_mode", "none")
            what_failed.append(
                f"- **{obs['theme']}** — failure mode: {fm} "
                f"(score {obs['crowd_signal_quality_score']}, "
                f"grade {obs['source_coverage_grade']})"
            )

    lines.append("## What Worked")
    lines.append("")
    lines.extend(what_worked if what_worked else ["No useful signals with reviewed outcomes this month."])
    lines += ["", "---", "", "## What Failed", ""]
    lines.extend(what_failed if what_failed else ["No failed signals with reviewed outcomes this month."])
    lines += ["", "---", ""]

    # Source-class lessons
    lines += ["## Source-Class Lessons", "", "| Source class | Signals | Useful | Mixed | Not useful |", "|---|---:|---:|---:|---:|"]
    sc_stats: dict[str, dict] = {}
    for obs, out in flat_outcomes:
        usefulness = out.get("signal_usefulness", "unknown")
        for sc in obs.get("source_classes", []):
            if sc not in sc_stats:
                sc_stats[sc] = {"total": 0, "useful": 0, "mixed": 0, "not_useful": 0}
            sc_stats[sc]["total"] += 1
            if usefulness in sc_stats[sc]:
                sc_stats[sc][usefulness] += 1
    if sc_stats:
        for sc, s in sorted(sc_stats.items()):
            lines.append(f"| {sc} | {s['total']} | {s['useful']} | {s['mixed']} | {s['not_useful']} |")
    else:
        lines.append("| — | 0 | 0 | 0 | 0 |")
    lines += ["", "---", ""]

    # Trajectory lessons
    lines += ["## Trajectory Lessons", "", "| Trajectory | Signals | Correct | Incorrect / Unknown |", "|---|---:|---:|---:|"]
    traj_stats: dict[str, dict] = {}
    for obs, out in flat_outcomes:
        traj = obs.get("signal_trajectory", "unknown")
        traj_stats.setdefault(traj, {"total": 0, "correct": 0, "not_correct": 0})
        traj_stats[traj]["total"] += 1
        tc = _bool_str(str(out.get("trajectory_correct", "unknown")))
        if tc is True:
            traj_stats[traj]["correct"] += 1
        else:
            traj_stats[traj]["not_correct"] += 1
    if traj_stats:
        for traj, s in sorted(traj_stats.items()):
            lines.append(f"| {traj} | {s['total']} | {s['correct']} | {s['not_correct']} |")
    else:
        lines.append("| — | 0 | 0 | 0 |")
    lines += ["", "---", ""]

    # Failure modes
    lines += ["## Failure Modes", "", "| Failure mode | Count |", "|---|---:|"]
    fm_counts: dict[str, int] = {}
    for _, out in flat_outcomes:
        fm = out.get("failure_mode", "none")
        fm_counts[fm] = fm_counts.get(fm, 0) + 1
    if fm_counts:
        for fm, count in sorted(fm_counts.items(), key=lambda x: -x[1]):
            lines.append(f"| {fm} | {count} |")
    else:
        lines.append("| none | 0 |")
    lines += ["", "---", ""]

    # Signals to continue monitoring
    lines += ["## Signals to Continue Monitoring", ""]
    if unreviewed_obs:
        for o in unreviewed_obs:
            lines.append(f"- {o['signal_id']} (score {o.get('crowd_signal_quality_score', '?')}, trajectory {o.get('signal_trajectory', '?')})")
    else:
        lines.append("None — all signals reviewed.")
    lines += ["", "---", ""]

    # Signals to retire
    lines += ["## Signals to Retire", ""]
    retire = [
        obs for obs, out in flat_outcomes
        if out.get("signal_usefulness") == "not_useful"
        and out.get("failure_mode", "none") != "none"
    ]
    if retire:
        for o in retire:
            lines.append(f"- {o['signal_id']}: {o['theme']}")
    else:
        lines.append("None flagged for retirement this month.")
    lines += ["", "---", ""]

    # Suggested playbook updates
    lines += [
        "## Suggested Playbook Updates",
        "",
        "These are suggestions only. Human approval required.",
        "Run `python csi.py playbook` to generate a full playbook from all accumulated data.",
        "",
    ]
    suggestions = _generate_review_suggestions(flat_outcomes, fm_counts, sc_stats)
    lines.extend(suggestions if suggestions else ["No patterns strong enough to suggest updates this month."])
    lines += ["", "---", ""]

    # Rates
    if flat_outcomes:
        traj_total = sum(s["total"] for s in traj_stats.values())
        traj_correct = sum(s["correct"] for s in traj_stats.values())
        traj_rate = round(traj_correct / traj_total * 100, 1) if traj_total else 0

        mainstreamed = sum(1 for _, out in flat_outcomes if _bool_str(str(out.get("narrative_mainstreamed", "false"))) is True)
        mainstreaming_rate = round(mainstreamed / signals_reviewed * 100, 1) if signals_reviewed else 0

        confirmed = sum(1 for _, out in flat_outcomes if _bool_str(str(out.get("catalyst_occurred", "false"))) is True)
        confirmation_rate = round(confirmed / signals_reviewed * 100, 1) if signals_reviewed else 0

        lines += [
            "## Signal Rates",
            "",
            f"- Trajectory accuracy rate: {traj_rate}%",
            f"- Narrative mainstreaming rate: {mainstreaming_rate}%",
            f"- Event confirmation rate: {confirmation_rate}%",
            "",
            "---",
            "",
        ]

    lines += [
        "## Non-Advisory Boundary",
        "",
        NON_ADVISORY_BOUNDARY,
    ]

    return "\n".join(lines)


def _generate_review_suggestions(
    flat_outcomes: list[tuple],
    fm_counts: dict[str, int],
    sc_stats: dict[str, dict],
) -> list[str]:
    suggestions = []

    if fm_counts.get("hype", 0) >= 2:
        suggestions.append("- Consider strengthening meme/hype penalty — multiple signals failed due to hype.")
    if fm_counts.get("single_source", 0) >= 2:
        suggestions.append("- Consider raising single-source penalty — multiple signals failed due to source concentration.")
    if fm_counts.get("priced_in", 0) >= 2:
        suggestions.append("- Consider adding earlier priced-in detection — multiple signals failed post price-move.")
    if fm_counts.get("wrong_transmission", 0) >= 2:
        suggestions.append("- Consider requiring explicit transmission mechanism evidence before analysis-ready classification.")
    if fm_counts.get("trajectory_wrong", 0) >= 2:
        suggestions.append("- Consider reviewing trajectory classifier — multiple trajectory predictions were incorrect.")

    for sc, stats in sc_stats.items():
        if stats["total"] >= 3 and stats["not_useful"] / stats["total"] >= 0.67:
            suggestions.append(f"- Source class `{sc}` had high not-useful rate — consider reviewing its scoring weight.")

    return suggestions


# ---------------------------------------------------------------------------
# Command: playbook
# ---------------------------------------------------------------------------


def cmd_playbook(
    data_dir: str = "data/csi",
    output_path: str = "playbooks/crowd-signal-playbook.md",
) -> str:
    all_obs = load_all_observations(data_dir)
    all_out = load_all_outcomes(data_dir)
    by_id = _outcomes_by_id(all_out)

    reviewed_pairs = []
    for obs in all_obs:
        outs = by_id.get(obs["signal_id"], [])
        if outs:
            reviewed_pairs.append((obs, outs[-1]))

    md = _build_playbook_md(reviewed_pairs)

    _ensure_dir(str(Path(output_path).parent))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

    return f"Playbook written to: {output_path}"


def _build_playbook_md(reviewed_pairs: list[tuple]) -> str:
    MIN_TENTATIVE = 5
    MIN_STRONG = 20
    n = len(reviewed_pairs)

    header = [
        "# Crowd Signal Playbook",
        "",
        f"Generated from {n} reviewed signal observation(s).",
        f"Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "",
        "---",
        "",
        "## Purpose",
        "",
        "This playbook records which crowd-signal patterns have historically been useful "
        "for identifying real narratives, catalysts, trajectories, source combinations, "
        "and market-transmission mechanisms.",
        "",
        "It is not an investment playbook.",
        "",
        f"## {PLAYBOOK_BOUNDARY.split(chr(10))[0]}",
        "",
        PLAYBOOK_BOUNDARY,
        "",
        "---",
        "",
    ]

    if n < MIN_TENTATIVE:
        body = [
            "## Status: Insufficient Data",
            "",
            f"Insufficient reviewed observations to generate durable playbook rules.",
            f"",
            f"Minimum recommended threshold:",
            f"- {MIN_TENTATIVE} reviewed signals for tentative lessons",
            f"- {MIN_STRONG} reviewed signals for stronger patterns",
            f"",
            f"Current reviewed observations: {n}",
            f"",
            "Continue running `observe` and `outcome` to build the dataset.",
        ]
        footer = _playbook_footer()
        return "\n".join(header + body + footer)

    # Aggregate patterns
    useful_pairs = [(o, out) for o, out in reviewed_pairs if out.get("signal_usefulness") == "useful"]
    failed_pairs = [(o, out) for o, out in reviewed_pairs if out.get("signal_usefulness") == "not_useful"]

    # Source class analysis
    sc_useful: dict[str, int] = {}
    sc_total: dict[str, int] = {}
    for obs, out in reviewed_pairs:
        usefulness = out.get("signal_usefulness", "unknown")
        for sc in obs.get("source_classes", []):
            sc_total[sc] = sc_total.get(sc, 0) + 1
            if usefulness == "useful":
                sc_useful[sc] = sc_useful.get(sc, 0) + 1

    # Trajectory analysis
    traj_correct: dict[str, int] = {}
    traj_total: dict[str, int] = {}
    for obs, out in reviewed_pairs:
        traj = obs.get("signal_trajectory", "unknown")
        traj_total[traj] = traj_total.get(traj, 0) + 1
        if _bool_str(str(out.get("trajectory_correct", "false"))) is True:
            traj_correct[traj] = traj_correct.get(traj, 0) + 1

    # Failure modes
    fm_counts: dict[str, int] = {}
    for _, out in reviewed_pairs:
        fm = out.get("failure_mode", "none")
        fm_counts[fm] = fm_counts.get(fm, 0) + 1

    # Grade usefulness
    grade_useful: dict[str, int] = {}
    grade_total: dict[str, int] = {}
    for obs, out in reviewed_pairs:
        grade = obs.get("source_coverage_grade", "?")
        grade_total[grade] = grade_total.get(grade, 0) + 1
        if out.get("signal_usefulness") == "useful":
            grade_useful[grade] = grade_useful.get(grade, 0) + 1

    confidence_note = "tentative" if n < MIN_STRONG else "based on sufficient observations"

    body = [
        f"## Data Confidence: {confidence_note} ({n} reviewed observations)",
        "",
        "---",
        "",
        "## Current Best Signal Patterns",
        "",
    ]

    if useful_pairs:
        for obs, _ in useful_pairs[:10]:
            body.append(
                f"- Score {obs['crowd_signal_quality_score']}, "
                f"grade {obs['source_coverage_grade']}, "
                f"trajectory {obs['signal_trajectory']}: "
                f"{obs['theme']}"
            )
    else:
        body.append("No useful patterns identified yet.")

    body += ["", "---", "", "## Signal Patterns That Failed", ""]
    if failed_pairs:
        for obs, out in failed_pairs[:10]:
            body.append(
                f"- **{obs['theme']}** — failure mode: {out.get('failure_mode', 'unknown')} "
                f"(score {obs['crowd_signal_quality_score']}, grade {obs['source_coverage_grade']})"
            )
    else:
        body.append("No failed patterns identified yet.")

    body += ["", "---", "", "## Source-Class Lessons", "", "| Source class | Signals | Useful | Useful rate |", "|---|---:|---:|---:|"]
    for sc in sorted(sc_total.keys()):
        total = sc_total[sc]
        useful_n = sc_useful.get(sc, 0)
        rate = round(useful_n / total * 100) if total else 0
        body.append(f"| {sc} | {total} | {useful_n} | {rate}% |")

    body += ["", "---", "", "## Trajectory Lessons", "", "| Trajectory | Signals | Correct | Accuracy |", "|---|---:|---:|---:|"]
    for traj in sorted(traj_total.keys()):
        total = traj_total[traj]
        correct = traj_correct.get(traj, 0)
        rate = round(correct / total * 100) if total else 0
        body.append(f"| {traj} | {total} | {correct} | {rate}% |")

    body += ["", "---", "", "## Penalty Lessons", ""]
    penalty_lessons = []
    if fm_counts.get("hype", 0) / n >= 0.2:
        penalty_lessons.append("- Hype failure mode is significant — meme/hype penalty may be under-applied.")
    if fm_counts.get("single_source", 0) / n >= 0.2:
        penalty_lessons.append("- Single-source failures are common — strengthen source independence requirements.")
    if fm_counts.get("priced_in", 0) / n >= 0.2:
        penalty_lessons.append("- Priced-in failures are common — add earlier market-data source requirements.")
    body.extend(penalty_lessons if penalty_lessons else ["No strong penalty lessons identified from current data."])

    body += ["", "---", "", "## Scoring Adjustments to Consider", "", "These require human review and approval.", ""]
    for sc in sorted(sc_total.keys()):
        total = sc_total[sc]
        if total >= 3:
            useful_n = sc_useful.get(sc, 0)
            rate = useful_n / total
            if rate <= 0.25:
                body.append(f"- Consider reducing weight for `{sc}` sources — low historical usefulness ({round(rate*100)}%).")
            elif rate >= 0.75:
                body.append(f"- `{sc}` sources show high usefulness ({round(rate*100)}%) — weight is appropriate.")

    body += ["", "---", "", "## Evidence Requirements to Strengthen", ""]
    ev_suggestions = []
    if fm_counts.get("no_catalyst", 0) / n >= 0.2:
        ev_suggestions.append("- Require explicit catalyst date or event in evidence before analysis-ready classification.")
    if fm_counts.get("wrong_transmission", 0) / n >= 0.2:
        ev_suggestions.append("- Require explicit transmission mechanism evidence (earnings, margins, supply/demand).")
    body.extend(ev_suggestions if ev_suggestions else ["No strong evidence-requirement changes indicated from current data."])

    body += [
        "",
        "---",
        "",
        "## Human-Approved Updates Needed",
        "",
        "The tool suggests playbook updates. It does not automatically change scoring weights.",
        "All scoring changes to `csi.py` require human review before editing.",
        "",
        "---",
        "",
    ]

    return "\n".join(header + body + _playbook_footer())


def _playbook_footer() -> list[str]:
    return [
        "",
        "---",
        "",
        "## Non-Advisory Boundary",
        "",
        PLAYBOOK_BOUNDARY,
    ]
