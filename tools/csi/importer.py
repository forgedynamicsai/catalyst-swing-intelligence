"""
Markdown evidence table importer.

Converts LLM-produced markdown tables into CSI evidence CSV format.

Workflow:
  LLM searches open web → LLM writes markdown evidence table
  → CLI imports to CSV → validate → score
"""

import csv
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Header alias normalization
# ---------------------------------------------------------------------------

HEADER_ALIASES = {
    "source": "source_name",
    "url": "source_url",
    "class": "source_class",
    "date": "source_date",
    "type": "source_type",
    "independence": "independence_rating",
    "quality": "evidence_quality",
    "duplicate": "is_duplicate",
}

# Documented defaults for missing optional values
IMPORT_DEFAULTS = {
    "source_url": "",
    "source_date": "",
    "source_type": "unknown",
    "independence_rating": "0",
    "evidence_quality": "0",
    "specificity": "0",
    "catalyst_alignment": "0",
    "dissent_quality": "0",
    "time_signal": "0",
    "is_duplicate": "false",
    "notes": "imported from markdown; review required",
}

REQUIRED_FOR_IMPORT = {"claim", "source_name"}


def _normalize_header(h: str) -> str:
    """Map a raw markdown header cell to a canonical CSI column name."""
    h = h.strip().lower().replace(" ", "_").replace("-", "_")
    return HEADER_ALIASES.get(h, h)


# ---------------------------------------------------------------------------
# Markdown table parser (line-based, no external deps)
# ---------------------------------------------------------------------------


def parse_markdown_table(text: str) -> tuple[list[str], list[dict]]:
    """
    Parse the first markdown table in text that looks like an evidence table.
    Returns (normalized_headers, rows).
    """
    lines = text.splitlines()
    in_table = False
    headers: list[str] = []
    rows: list[dict] = []

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break  # end of table
            continue

        cells = [c.strip() for c in stripped.strip("|").split("|")]

        if not in_table:
            # First pipe-line is the header row
            headers = [_normalize_header(c) for c in cells if c or True]
            in_table = True
            continue

        # Skip separator row (dashes/colons only)
        if all(re.match(r"^[-:\s]*$", c) for c in cells):
            continue

        # Data row — zip with headers, allow short rows
        row: dict[str, str] = {}
        for j, col in enumerate(headers):
            row[col] = cells[j].strip() if j < len(cells) else ""
        rows.append(row)

    return headers, rows


# ---------------------------------------------------------------------------
# Default application
# ---------------------------------------------------------------------------


def _apply_defaults(row: dict, used_defaults: dict) -> dict:
    """Fill missing optional fields with documented defaults."""
    result = dict(row)
    for col, default in IMPORT_DEFAULTS.items():
        if col not in result or not str(result.get(col, "")).strip():
            result[col] = default
            used_defaults[col] = used_defaults.get(col, 0) + 1
    return result


# ---------------------------------------------------------------------------
# Import command
# ---------------------------------------------------------------------------


def import_md(
    md_path: str,
    output_path: str,
    append: bool = False,
) -> tuple[str, int]:
    """
    Import a markdown evidence table to a CSI evidence CSV.
    Returns (output_string, exit_code). Exit code 0 = success.
    """
    try:
        text = Path(md_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: file not found: {md_path}", 1
    except Exception as e:
        return f"Error reading {md_path}: {e}", 1

    headers, rows = parse_markdown_table(text)

    if not rows:
        return (
            "Error: no markdown evidence table found in input.\n"
            "Ensure the file contains a pipe-delimited markdown table."
        ), 1

    # Check required fields
    found_cols = set(headers)
    missing = REQUIRED_FOR_IMPORT - found_cols
    if missing:
        return (
            f"Error: required column(s) not found in markdown table: "
            f"{', '.join(sorted(missing))}.\n"
            f"Ensure the table has 'claim' and 'source_name' columns "
            f"(or aliases 'source')."
        ), 1

    # Check output path collision
    out = Path(output_path)
    if out.exists() and not append:
        return (
            f"Error: output file already exists: {output_path}\n"
            f"Use --append to add rows, or remove the file first."
        ), 1

    # Apply defaults
    used_defaults: dict[str, int] = {}
    final_rows = [_apply_defaults(row, used_defaults) for row in rows]

    # Write CSV
    # Import EVIDENCE_COLUMNS from sibling module
    import sys, os
    _here = os.path.dirname(os.path.abspath(__file__))
    if _here not in sys.path:
        sys.path.insert(0, _here)
    from csi import EVIDENCE_COLUMNS

    out.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if (append and out.exists()) else "w"
    write_header = not (append and out.exists())

    with open(output_path, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EVIDENCE_COLUMNS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        for row in final_rows:
            for col in EVIDENCE_COLUMNS:
                if col not in row:
                    row[col] = ""
            writer.writerow(row)

    # Run validation on imported rows
    from validation import validate_rows
    errors, warnings = validate_rows(final_rows)

    lines = [f"Imported {len(final_rows)} evidence row(s) to {output_path}."]

    if used_defaults:
        lines.append("\nDefaults applied (review required):")
        for col, count in sorted(used_defaults.items()):
            lines.append(f"  - {count} row(s) used default {col}={IMPORT_DEFAULTS[col]!r}.")

    if errors:
        lines.append(f"\nValidation result: FAIL ({len(errors)} error(s)).")
        lines.extend(f"  - {e}" for e in errors)
        return "\n".join(lines), 1

    if warnings:
        lines.append(
            f"\nValidation result: PASS WITH WARNINGS ({len(warnings)} warning(s))."
        )
        lines.extend(f"  - {w}" for w in warnings)
    else:
        lines.append("\nValidation result: PASS.")

    lines.append(f"\nNext:")
    lines.append(f"  python tools/csi/csi.py score {output_path}")
    lines.append(f"  python tools/csi/csi.py report {output_path} --output report.md")
    return "\n".join(lines), 0
