"""
Guided terminal workflow wizard for CSI CLI.

Thin harness over existing deterministic scoring, validation, and memory code.
Does not perform web searches or make investment recommendations.

Crowd Signal Quality != Security Risk != Trade Decision
"""

import os
import sys
from datetime import datetime
from pathlib import Path

WIZARD_BANNER = """\
=== Catalyst Swing Intelligence Wizard ===

This tool evaluates Crowd Signal Quality.

It does NOT provide:
  - financial advice
  - buy/sell/hold recommendations
  - price targets
  - position sizing
  - investment recommendations

Crowd Signal Quality != Security Risk != Trade Decision"""


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------


def _prompt(msg: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"{msg}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nWizard cancelled.")
        sys.exit(0)
    return val or default


def _confirm(msg: str, default: bool = True) -> bool:
    hint = "[Y/n]" if default else "[y/N]"
    try:
        val = input(f"{msg} {hint}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nWizard cancelled.")
        sys.exit(0)
    if not val:
        return default
    return val in ("y", "yes")


def _slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")[:60]


# ---------------------------------------------------------------------------
# Dry-run plan (non-interactive preview — also used for testing)
# ---------------------------------------------------------------------------


def dry_run_plan(
    theme: str,
    evidence_path: str,
    data_dir: str,
    reports_dir: str,
) -> str:
    """Return the planned workflow as a string without any interactive prompts."""
    slug = _slugify(theme)
    report_path = f"{reports_dir}/{slug}-report.md"
    lines = [
        WIZARD_BANNER,
        "",
        f"Theme:         {theme}",
        f"Evidence file: {evidence_path}",
        f"Report path:   {report_path}",
        "",
        "Planned workflow (dry-run — no prompts, no side effects):",
        "  1. Generate search queries",
        "  2. Create evidence CSV template",
        "  3. [Pause for research]",
        "  4. Validate evidence CSV",
        "  5. Run deterministic scoring",
        "  6. Generate markdown report",
        "  7. Save observation to local memory",
        "  8. Print outcome-review next commands",
        "",
        "Commands in order:",
        f"  python tools/csi/csi.py template --output {evidence_path}",
        f"  python tools/csi/csi.py validate {evidence_path}",
        f"  python tools/csi/csi.py score {evidence_path}",
        f"  python tools/csi/csi.py report {evidence_path} --output {report_path}",
        f'  python tools/csi/csi.py observe {evidence_path} --theme "{theme}"',
        "  python tools/csi/csi.py outcome SIGNAL_ID --usefulness unknown --failure-mode other",
        "  python tools/csi/csi.py monthly-review --month YYYY-MM",
        "  python tools/csi/csi.py playbook",
        "",
        "The wizard does not perform web searches or make recommendations.",
        "Crowd Signal Quality != Security Risk != Trade Decision",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Next-steps footer
# ---------------------------------------------------------------------------


def _next_steps_text(signal_id: str = "") -> str:
    sid = signal_id or "SIGNAL_ID"
    now = datetime.now()
    lines = [
        "── Next Steps ──────────────────────────────────────────────────",
        "After reviewing the signal outcome, run:",
        "",
        f"  python tools/csi/csi.py outcome {sid} \\",
        "    --event-confirmed unknown \\",
        "    --narrative-mainstreamed unknown \\",
        "    --trajectory-correct unknown \\",
        "    --catalyst-occurred unknown \\",
        "    --transmission-confirmed unknown \\",
        "    --usefulness unknown \\",
        "    --failure-mode other \\",
        '    --notes "Outcome not yet reviewed."',
        "",
        f"  python tools/csi/csi.py monthly-review --month {now.strftime('%Y-%m')}",
        "  python tools/csi/csi.py playbook",
        "",
        "The wizard evaluates Crowd Signal Quality only.",
        "It does not provide financial advice or investment recommendations.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main wizard
# ---------------------------------------------------------------------------


def run_wizard(
    theme: str = "",
    evidence_path: str = "",
    dry_run: bool = False,
    data_dir: str = "data/csi",
    reports_dir: str = "reports/csi",
) -> None:
    """
    Run the guided CSI workflow.
    dry_run=True: print planned workflow without any prompts or side effects.
    """
    if dry_run:
        ev = evidence_path or "evidence.csv"
        th = theme or "Fictional AI infrastructure signal"
        print(dry_run_plan(th, ev, data_dir, reports_dir))
        return

    # ── Banner ─────────────────────────────────────────────────────────────
    print(WIZARD_BANNER)
    print()

    # ── Step 1: Theme ──────────────────────────────────────────────────────
    if not theme:
        theme = _prompt("Enter the crowd narrative or catalyst theme")
    else:
        print(f"Theme: {theme}")
    if not theme:
        print("No theme provided. Exiting.")
        sys.exit(1)
    print()

    # ── Step 2: Search queries ─────────────────────────────────────────────
    print("── Step 2: Search Queries ──────────────────────────────────────")
    # Lazy import to keep harness thin
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import csi as _csi
    print(_csi.cmd_queries(theme))
    print()
    print("Use these queries with your LLM/search agent or open-web search.")
    print("Do not invent sources.")
    print("After searching, enter one row per source or claim into the evidence CSV.")
    print()

    # ── Step 3: Evidence CSV ───────────────────────────────────────────────
    print("── Step 3: Evidence CSV ────────────────────────────────────────")
    if not evidence_path:
        evidence_path = "evidence.csv"

    ev = Path(evidence_path)
    if ev.exists():
        use_existing = _confirm(f"{evidence_path} already exists. Use it?", default=True)
        if not use_existing:
            evidence_path = _prompt("Evidence CSV path", default="evidence.csv")
            ev = Path(evidence_path)
    else:
        create = _confirm(
            f"Create evidence CSV template at {evidence_path}?", default=True
        )
        if create:
            print(_csi.cmd_template(evidence_path))

    print(f"\nEvidence file: {evidence_path}")
    print("You can also run:")
    print(f"  python tools/csi/csi.py import-md evidence.md --output {evidence_path}")
    print()

    # ── Step 4: Pause for research ─────────────────────────────────────────
    print("── Step 4: Research Pause ──────────────────────────────────────")
    print(f"Open {evidence_path} and add one row per source or claim.")
    print("Then return here and press Enter to continue.")
    print()
    cont = _confirm(
        "Ready to continue with validation and scoring?", default=True
    )
    if not cont:
        print(f"\nPaused. Resume when ready:")
        print(f"  python tools/csi/csi.py validate {evidence_path}")
        print(f"  python tools/csi/csi.py score {evidence_path}")
        return

    # ── Step 5: Validate ───────────────────────────────────────────────────
    print()
    print("── Step 5: Validation ──────────────────────────────────────────")
    import validation as _val
    val_output, exit_code = _val.cmd_validate(evidence_path)
    print(val_output)
    if exit_code != 0:
        print(f"\nValidation failed. Fix {evidence_path}, then run:")
        print(f"  python tools/csi/csi.py validate {evidence_path}")
        sys.exit(1)
    print()

    # ── Step 6: Score ──────────────────────────────────────────────────────
    print("── Step 6: Score ───────────────────────────────────────────────")
    print(_csi.cmd_score(evidence_path))
    print()

    # ── Step 7: Report ─────────────────────────────────────────────────────
    print("── Step 7: Report ──────────────────────────────────────────────")
    slug = _slugify(theme)
    default_report = f"{reports_dir}/{slug}-report.md"
    report_path = _prompt("Save report to", default=default_report)
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    print(_csi.cmd_report(evidence_path, report_path, theme))
    print()

    # ── Step 8: Save observation ───────────────────────────────────────────
    print("── Step 8: Save Observation ────────────────────────────────────")
    save_obs = _confirm(
        "Save this scored signal as a local observation?", default=True
    )
    signal_id = ""
    if save_obs:
        import memory as _mem
        obs_output = _mem.cmd_observe(
            evidence_path, theme,
            data_dir=data_dir,
            reports_dir=reports_dir,
        )
        print(obs_output)
        for line in obs_output.splitlines():
            if line.strip().startswith("Signal ID:"):
                signal_id = line.split(":", 1)[1].strip()
    print()

    # ── Step 9: Next steps ─────────────────────────────────────────────────
    print(_next_steps_text(signal_id))
