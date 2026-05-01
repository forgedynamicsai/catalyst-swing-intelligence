# CSI — Crowd Signal Intelligence CLI

Minimal, search-first crowd signal scoring tool.

**Zero required paid APIs. Zero required data subscriptions.**

---

## Guided Workflow

New users: run the wizard to walk through the full workflow step by step.

```bash
python tools/csi/csi.py wizard
```

The wizard walks through:

1. Theme entry
2. Search query generation
3. Evidence CSV creation
4. Research pause (open-web or LLM search)
5. Validation
6. Scoring
7. Report generation
8. Observation storage
9. Outcome-review next steps

For a non-interactive preview of the planned workflow:

```bash
python tools/csi/csi.py wizard --theme "AI data center power scarcity" --dry-run
```

---

## Validate Evidence

Before scoring, validate that your evidence CSV is well-formed:

```bash
python tools/csi/csi.py validate evidence.csv
```

Use `--strict` to treat warnings as errors:

```bash
python tools/csi/csi.py validate evidence.csv --strict
```

---

## Import Markdown Evidence

LLMs and search agents produce markdown tables more reliably than CSV.
Import a markdown evidence table directly:

```bash
python tools/csi/csi.py import-md evidence.md --output evidence.csv
```

Use `--append` to add rows to an existing CSV:

```bash
python tools/csi/csi.py import-md more_evidence.md --output evidence.csv --append
```

See `tools/csi/sample_evidence.md` for the expected markdown table format.

---

## Purpose

This tool implements the deterministic scoring model from `docs/crowd-signal-scoring.md`
as a local Python CLI. It supports the manual research workflow:

1. Generate source-targeted search queries for a theme.
2. Collect evidence rows into a CSV file.
3. Score the evidence deterministically.
4. Generate a markdown crowd signal report.

The tool scores **crowd signal quality** — not expected return, security risk, or
whether any user should buy, sell, or hold anything.

---

## Requirements

- Python 3.10+ (standard library only)
- No pip installs required

---

## From Evidence Harvest to Memory Flywheel

The intended workflow is:

1. Use the agent skill (`/catalyst-swing-intelligence` or `/swing-intelligence`) to generate a search-first evidence-harvest plan.
2. Search the open web or gather user-provided public sources.
3. Convert each source into `evidence.csv` using the CSI schema.
4. Run deterministic scoring.
5. Generate a markdown report.
6. Save the report as a local observation.
7. Add an outcome review later.
8. Generate monthly effectiveness reviews.
9. Update the crowd-signal playbook.

```bash
python tools/csi/csi.py template --output evidence.csv
python tools/csi/csi.py score evidence.csv
python tools/csi/csi.py report evidence.csv --output report.md
python tools/csi/csi.py observe evidence.csv --theme "[THEME]"
python tools/csi/csi.py list
python tools/csi/csi.py outcome SIGNAL_ID --event-confirmed unknown --narrative-mainstreamed unknown --trajectory-correct unknown --catalyst-occurred unknown --transmission-confirmed unknown --usefulness unknown --failure-mode other
python tools/csi/csi.py monthly-review --month YYYY-MM
python tools/csi/csi.py playbook
```

The memory flywheel evaluates crowd-signal usefulness, not investment performance.

---

## Commands

```bash
# Generate search queries for a theme
python tools/csi/csi.py queries "AI data center power scarcity"

# Create a blank evidence CSV template
python tools/csi/csi.py template --output evidence.csv

# Score a filled-in evidence CSV
python tools/csi/csi.py score tools/csi/sample_evidence.csv

# Generate a markdown crowd signal report
python tools/csi/csi.py report tools/csi/sample_evidence.csv --output report.md

# Run a built-in demo (fictional data)
python tools/csi/csi.py demo

# --- Memory Flywheel ---

# Save a scored observation to local memory
python tools/csi/csi.py observe tools/csi/sample_evidence.csv --theme "AI infrastructure"

# List stored observations
python tools/csi/csi.py list

# List observations for a specific month
python tools/csi/csi.py list --month 2026-05

# Attach an outcome review to an observation
python tools/csi/csi.py outcome SIGNAL_ID \
  --event-confirmed true \
  --narrative-mainstreamed true \
  --trajectory-correct true \
  --catalyst-occurred true \
  --transmission-confirmed partial \
  --usefulness useful \
  --failure-mode none \
  --notes "Fictional outcome review."

# Generate monthly effectiveness review
python tools/csi/csi.py monthly-review --month 2026-05

# Generate crowd signal playbook from accumulated data
python tools/csi/csi.py playbook
```

---

## Evidence CSV Schema

| Column | Type | Range | Description |
|---|---|---|---|
| claim | string | — | What the source claims |
| source_name | string | — | Name of the source |
| source_url | string | — | URL of the source |
| source_class | string | see below | Category of the source |
| source_date | string | — | Publication date |
| source_type | string | — | article / transcript / filing / social / etc. |
| independence_rating | int | 0–20 | How independent from other sources |
| evidence_quality | int | 0–20 | How well-evidenced (filings, transcripts, data) |
| specificity | int | 0–20 | How specific (mechanism, not just ticker) |
| catalyst_alignment | int | 0–10 | Alignment to a dated catalyst |
| dissent_quality | int | 0–5 | Quality of opposing evidence in this row |
| time_signal | int | 0–10 | Is attention increasing over time? |
| is_duplicate | bool | true/false | Is this row a copy/echo of another? |
| notes | string | — | Free text; also parsed for penalty markers |

### Source Classes

```
primary_filing      earnings_transcript   company_ir
major_news          trade_publication     investing_forum
social_media        prediction_market     pundit
whale_positioning   copy_trading          market_data
unknown
```

---

## Scoring Model

Implements the 100-point Crowd Signal Quality model from `docs/crowd-signal-scoring.md`.

**Base components:**

| Component | Max |
|---|---:|
| Signal volume (inferred from row count) | 15 |
| Source independence | 20 |
| Specificity | 20 |
| Evidence quality | 20 |
| Time acceleration | 10 |
| Catalyst alignment | 10 |
| Dissent quality | 5 |

**Penalties** (detected from `notes` column text and data patterns):

| Penalty | Max | Trigger |
|---|---:|---|
| Meme/hype | −15 | "meme", "yolo", "moon", "guaranteed", "rocket" |
| Crowding | −15 | "crowded", "consensus", "everyone knows", "saturated" |
| Price moved | −20 | "already moved", "priced in", "gap up", "extended" |
| Loose ticker basket | −10 | "basket", "loose", "unclear ticker" |
| Single source | −20 | All rows from one source class or name |
| Duplicate | −10 | High `is_duplicate` ratio |
| Unknown source | −10 | High `unknown` source class ratio |

**Final score:** `max(0, min(100, base − penalties))`

### Source Coverage Grade

| Grade | Criteria |
|---|---|
| A | Primary/factual + crowd/forum + prediction/market/positioning + dissent |
| B | Primary/factual + crowd/forum + news or prediction/market |
| C | Crowd/forum + news only — labeled *provisional / source-limited* |
| D | Single source class — no full-confidence score |
| F | No evidence — no score |

---

## Memory Flywheel — Local Data Files

Generated at runtime. Gitignored. Not for public repo.

| Path | Contents |
|---|---|
| `data/csi/observations.jsonl` | One scored observation per line |
| `data/csi/outcomes.jsonl` | One outcome review per line |
| `reports/csi/` | Saved markdown reports (one per observation) |
| `reviews/csi/` | Monthly effectiveness reviews |
| `playbooks/crowd-signal-playbook.md` | Generated playbook from accumulated data |

**Non-advisory boundary:** The memory flywheel evaluates crowd-signal usefulness.
It does not recommend purchases, investments, trades, position sizing,
or buy/sell/hold actions for any security.

**Signal classification uses `analysis-ready / monitor / reject`** (not `tradeable`).

---

## Limitations

- Notes-based penalty detection is keyword-matching only.
- Source quality ratings must be entered manually — no live data connections.
- Trajectory classification uses simple heuristics, not time-series analysis.
- This tool does not fetch prices, fundamentals, or real-time data.
- This is a decision-support aid. It does not replace judgment.
- Playbook suggestions require human review before any scoring changes.

---

## Example Output

See `tools/csi/sample_evidence.csv` and `tools/csi/sample_report.md` for a
worked fictional example (AI data center power demand theme).

---

## Legal

This tool is part of the `catalyst-swing-intelligence` project.
See `DISCLAIMER.md` for the full disclaimer.

**Crowd Signal Quality ≠ Security Risk ≠ Trade Decision**

This tool does not make buy/sell/hold recommendations.
