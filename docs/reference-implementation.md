# Reference Implementation

This document explains the low-cost reference implementation under `tools/csi/`.

---

## Why This Exists

The `catalyst-swing-intelligence` skill is a Claude Code skill — it lives in natural
language and runs inside an AI assistant. But a deterministic, auditable scoring
reference is useful for:

- Verifying that the skill's scoring behavior matches the documented model.
- Running the crowd signal workflow locally without an AI assistant.
- Using the scoring logic in automated pipelines or CI.
- Providing a concrete, testable artifact alongside the prose methodology.

---

## Search-First, Manual Workflow

The reference implementation is designed around a **search-first** workflow:

```
1. Identify a market theme.
2. Generate source-targeted search queries (no execution, no API calls).
3. Manually search and read sources.
4. Enter evidence rows into a CSV file.
5. Run the scorer to get a deterministic Crowd Signal Quality Score.
6. Generate a markdown report.
```

This keeps cost at $0 and makes the scoring process fully transparent and auditable.

---

## Zero Required Paid APIs

The tool uses only the Python standard library.

| Requirement | Status |
|---|---|
| Paid data subscriptions | Not required |
| Brokerage API | Not required |
| LLM API | Not required |
| Live price feed | Not required |
| External services | Not required |

Optional future connectors could add live data retrieval (e.g., free SEC EDGAR API,
free Reddit API, etc.), but these are not part of the reference implementation.

---

## Deterministic Scoring

All scoring is deterministic: given the same CSV input, the output is always identical.

This is intentional. Deterministic scoring allows:

- Reproducibility — the same evidence always produces the same score.
- Auditability — every score can be traced to specific evidence rows.
- Testing — automated tests can assert exact score behavior.
- Comparison — evidence can be updated and score changes tracked over time.

The scoring model implements the full 100-point model from `docs/crowd-signal-scoring.md`.

---

## Memory Flywheel

v0.4 adds a local memory flywheel built on top of the deterministic scoring engine.

```
Score signal → Save observation → Track outcome → Monthly review →
Suggested playbook updates → Better future crowd-signal assessment.
```

**What the flywheel learns:**

Which crowd-signal patterns were useful for identifying real narratives, catalysts,
trajectories, source combinations, and market-transmission mechanisms.

**What the flywheel does not learn:**

Which stocks to buy.

**Signal classification:** `analysis-ready / monitor / reject`

This replaces `tradeable / watchlist / reject` in all new outputs.
See `docs/memory-flywheel.md` for full definitions.

**Data files (all gitignored):**

```
data/csi/observations.jsonl
data/csi/outcomes.jsonl
reports/csi/
reviews/csi/
playbooks/crowd-signal-playbook.md
```

---

## Relationship to the Agent Skill

| Dimension | Agent Skill (`SKILL.md`) | Reference Implementation (`tools/csi/`) |
|---|---|---|
| Interface | Natural language via Claude | CLI + CSV |
| Evidence collection | AI-assisted research | Manual / agent-driven search |
| Scoring | Described in prose | Deterministic Python |
| Output | Markdown report in chat | Markdown file or stdout |
| API cost | Claude API | $0 (standard library only) |
| Best for | Guided research workflow | Batch scoring, CI, audit, offline use |

Both implement the same scoring model. The agent skill interprets evidence; the
reference implementation scores it deterministically once it has been collected.

---

## Optional Future Connectors

The reference implementation does not include live connectors, but the architecture
supports them. Future connectors could include:

- Free SEC EDGAR full-text search API
- Free Reddit API (rate-limited)
- Free prediction market APIs (Polymarket, Metaculus)
- Free news headline feeds (RSS, Google News)
- Local LLM for evidence extraction from raw text

Any connector added must preserve the zero-required-paid-API principle for the
base workflow.

---

## v0.5 Guided Terminal Workflow

v0.5 adds three operability commands on top of the v0.3/v0.4 scoring and memory engine:

| Command | Purpose |
|---|---|
| `wizard` | Guided step-by-step workflow — theme → queries → CSV → validate → score → report → observe |
| `validate` | Pre-flight policy gate — checks schema, ranges, source classes, booleans, advisory language |
| `import-md` | Converts LLM-produced markdown evidence tables into CSI evidence CSV |

**Architecture — thin harness, fat deterministic code:**

- `validation.py` — all validation logic (reused by wizard and import-md)
- `importer.py` — markdown parsing and CSV import (calls validation after import)
- `wizard.py` — thin orchestration harness over existing scoring, memory, and validation functions
- `csi.py` — command registration only; lazy imports keep the harness thin

The wizard does not perform web searches or make recommendations.

```bash
python tools/csi/csi.py wizard --dry-run
python tools/csi/csi.py validate evidence.csv
python tools/csi/csi.py import-md evidence.md --output evidence.csv
```

---

## Running Tests

```bash
python -m unittest discover -s tests
```

See `docs/testing-guide.md` for the full test checklist.

---

## Legal

Crowd Signal Quality ≠ Security Risk ≠ Trade Decision.

This tool does not make buy/sell/hold recommendations.
See `DISCLAIMER.md` for the full disclaimer.
