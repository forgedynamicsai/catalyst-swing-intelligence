"""
Evidence CSV validation — pre-flight policy gate before scoring.

All checks are deterministic. No network access required.
Policy-gate pattern: hard rules run in pure Python, fire before scoring,
cannot be overridden by any prompt.
"""

import csv
from pathlib import Path

# ---------------------------------------------------------------------------
# Schema constants (source of truth for validation)
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = [
    "claim", "source_name", "source_url", "source_class", "source_date",
    "source_type", "independence_rating", "evidence_quality", "specificity",
    "catalyst_alignment", "dissent_quality", "time_signal", "is_duplicate", "notes",
]

CRITICAL_FIELDS = ["claim", "source_name", "source_class", "source_date", "source_type"]

VALID_SOURCE_CLASSES = {
    "primary_filing", "earnings_transcript", "company_ir", "major_news",
    "trade_publication", "investing_forum", "social_media", "prediction_market",
    "pundit", "whale_positioning", "copy_trading", "market_data", "unknown",
}

NUMERIC_RANGES = {
    "independence_rating": (0, 20),
    "evidence_quality": (0, 20),
    "specificity": (0, 20),
    "catalyst_alignment": (0, 10),
    "dissent_quality": (0, 5),
    "time_signal": (0, 10),
}

BOOL_FIELDS = {"is_duplicate"}
TRUTHY = {"true", "yes", "1"}
FALSY = {"false", "no", "0"}

# Language that should not appear as recommendations in evidence rows
ADVISORY_MARKERS = [
    "buy now", "sell now", "hold this", "purchase shares", "invest in",
    "recommended company", "price target", "expected return", "guaranteed",
    "beats the market", "alpha",
]


# ---------------------------------------------------------------------------
# Core validation logic
# ---------------------------------------------------------------------------


def validate_rows(rows: list[dict]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a list of evidence row dicts."""
    errors: list[str] = []
    warnings: list[str] = []

    if not rows:
        errors.append("Evidence file is empty — no data rows found.")
        return errors, warnings

    # Column presence check (only needs to run once)
    cols = set(rows[0].keys())
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in cols]
    if missing_cols:
        for col in missing_cols:
            errors.append(f"Missing required column: {col}")
        # Can't validate rows if columns are missing
        return errors, warnings

    for i, row in enumerate(rows, start=1):
        # source_class validity
        sc = row.get("source_class", "").strip()
        if sc and sc not in VALID_SOURCE_CLASSES:
            errors.append(
                f"Row {i}: invalid source_class '{sc}'. "
                f"Valid: {', '.join(sorted(VALID_SOURCE_CLASSES))}."
            )

        # Numeric range checks
        for col, (lo, hi) in NUMERIC_RANGES.items():
            val = row.get(col, "").strip()
            if val:
                try:
                    v = int(val)
                    if not (lo <= v <= hi):
                        errors.append(
                            f"Row {i}: {col} must be {lo}–{hi}, got {v}."
                        )
                except ValueError:
                    errors.append(
                        f"Row {i}: {col} must be an integer, got '{val}'."
                    )

        # Boolean field check
        dup_raw = row.get("is_duplicate", "").strip()
        if dup_raw and dup_raw.lower() not in TRUTHY | FALSY:
            errors.append(
                f"Row {i}: is_duplicate must be true/false, got '{dup_raw}'."
            )

        # Critical empty field warnings
        for field in CRITICAL_FIELDS:
            if not row.get(field, "").strip():
                warnings.append(f"Row {i}: {field} is empty.")

        # source_url warning (not a hard error)
        if not row.get("source_url", "").strip():
            warnings.append(f"Row {i}: source_url is empty.")

        # Advisory language check
        text_to_check = (
            row.get("claim", "") + " " + row.get("notes", "")
        ).lower()
        for marker in ADVISORY_MARKERS:
            if marker in text_to_check:
                warnings.append(
                    f"Row {i}: text contains '{marker}'; "
                    f"ensure this is contextual evidence, not a recommendation."
                )

    return errors, warnings


def validate_file(path: str) -> tuple[list[dict], list[str], list[str]]:
    """Load a CSV and validate it. Returns (rows, errors, warnings)."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    errors, warnings = validate_rows(rows)
    return rows, errors, warnings


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------


def cmd_validate(path: str, strict: bool = False) -> tuple[str, int]:
    """
    Validate an evidence CSV.
    Returns (output_string, exit_code).
    Exit code 0 = pass or pass-with-warnings.
    Exit code 1 = fail (or strict pass-with-warnings).
    """
    try:
        rows, errors, warnings = validate_file(path)
    except FileNotFoundError:
        return f"Error: file not found: {path}", 1
    except Exception as e:
        return f"Error reading {path}: {e}", 1

    n = len(rows)

    if strict and warnings:
        errors = errors + [f"[strict] {w}" for w in warnings]
        warnings = []

    lines: list[str] = []

    if errors:
        lines.append("Validation result: FAIL")
        lines.append(f"\nRows checked: {n}")
        lines.append(f"Errors: {len(errors)}")
        lines.append(f"Warnings: {len(warnings)}")
        lines.append("\nErrors:")
        lines.extend(f"  - {e}" for e in errors)
        if warnings:
            lines.append("\nWarnings:")
            lines.extend(f"  - {w}" for w in warnings)
        return "\n".join(lines), 1

    if warnings:
        lines.append("Validation result: PASS WITH WARNINGS")
        lines.append(f"\nRows checked: {n}")
        lines.append("Errors: 0")
        lines.append(f"Warnings: {len(warnings)}")
        lines.append("\nWarnings:")
        lines.extend(f"  - {w}" for w in warnings)
    else:
        lines.append("Validation result: PASS")
        lines.append(f"\nRows checked: {n}")
        lines.append("Errors: 0  Warnings: 0")

    lines.append(f"\nNext:")
    lines.append(f"  python tools/csi/csi.py score {path}")
    lines.append(f"  python tools/csi/csi.py report {path} --output report.md")
    return "\n".join(lines), 0
