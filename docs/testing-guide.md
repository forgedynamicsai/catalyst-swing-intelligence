# Testing Guide

---

## Manual Skill Tests

Run these after any change to `skills/catalyst-swing-intelligence/SKILL.md`.

See `docs/evaluation-tests.md` for the full manual test suite.

---

## Reference Implementation Tests

Run these after any change to `tools/csi/csi.py`.

### Automated Tests

```bash
python -m unittest discover -s tests
```

Expected: all tests pass. No failures.

### Manual CLI Smoke Tests

```bash
# Query generation — should print search queries, zero network calls
python tools/csi/csi.py queries "AI data center power scarcity"

# Template — should write a CSV with all required columns
python tools/csi/csi.py template --output /tmp/csi_evidence.csv

# Score — should print score breakdown for sample evidence
python tools/csi/csi.py score tools/csi/sample_evidence.csv

# Report — should write a markdown report
python tools/csi/csi.py report tools/csi/sample_evidence.csv --output /tmp/csi_report.md

# Demo — should print a full fictional crowd signal report
python tools/csi/csi.py demo
```

### What to Verify

| Check | Expected |
|---|---|
| Score is 0–100 | Always |
| Empty evidence → grade F, no-evidence confidence | Always |
| Duplicate rows reduce score vs. clean rows | Always |
| Unknown source class reduces score | Always |
| Grade A requires primary + crowd + prediction + dissent | Always |
| Report contains "Not a buy/sell/hold recommendation" | Always |
| Disclaimer mentions NOT a buy/sell/hold score | Always |
| Demo output contains no private data (Arron, Carter, PCS) | Always |
| `queries` output contains "Cost: $0" | Always |

---

## Memory Flywheel Command Tests

Run these after any change to `tools/csi/memory.py`.

```bash
# Observe — score + save to local data dir
python tools/csi/csi.py observe tools/csi/sample_evidence.csv \
  --theme "Fictional AI infrastructure signal" \
  --data-dir /tmp/csi-data \
  --reports-dir /tmp/csi-reports

# List — show observations and outcome status
python tools/csi/csi.py list --data-dir /tmp/csi-data

# Outcome — attach outcome review (replace SIGNAL_ID from list output)
python tools/csi/csi.py outcome SIGNAL_ID \
  --event-confirmed true \
  --narrative-mainstreamed true \
  --trajectory-correct true \
  --catalyst-occurred true \
  --transmission-confirmed partial \
  --usefulness useful \
  --failure-mode none \
  --notes "Fictional outcome." \
  --data-dir /tmp/csi-data

# Monthly review
python tools/csi/csi.py monthly-review \
  --month 2026-05 \
  --data-dir /tmp/csi-data \
  --output /tmp/csi-review.md

# Playbook
python tools/csi/csi.py playbook \
  --data-dir /tmp/csi-data \
  --output /tmp/csi-playbook.md
```

### Memory Flywheel Verification Checklist

| Check | Expected |
|---|---|
| `observe` creates `observations.jsonl` | Always |
| `observe` creates report file in reports dir | Always |
| Duplicate theme → new ID with suffix (-2, -3) | Always |
| `list` shows "unreviewed" before outcome | Always |
| `list` shows "reviewed" after outcome | Always |
| `outcome` with unknown signal_id exits nonzero | Always |
| `monthly-review` with no data → valid empty-state markdown | Always |
| `playbook` with < 5 observations → "Insufficient data" message | Always |
| All outputs contain "Non-Advisory Boundary" | Always |
| No output contains "tradeable" or "watchlist" | Always |
| No output suggests purchases, investments, or companies to buy | Always |

---

## Test — Evidence Harvest Bridges to CSI CLI

Run these after any change to the crowd-scan output contract in `SKILL.md`
or to `examples/crowd-scan-example.md`.

```bash
python tools/csi/csi.py template --output /tmp/csi_evidence.csv
python tools/csi/csi.py score tools/csi/sample_evidence.csv
python tools/csi/csi.py report tools/csi/sample_evidence.csv --output /tmp/csi_report.md
python tools/csi/csi.py observe tools/csi/sample_evidence.csv \
  --theme "Fictional AI infrastructure signal" \
  --data-dir /tmp/csi-data \
  --reports-dir /tmp/csi-reports
python tools/csi/csi.py list --data-dir /tmp/csi-data
```

### What to verify

| Check | Expected |
|---|---|
| `SKILL.md` contains `Convert to CSI Evidence CSV` | Always |
| `SKILL.md` contains `python tools/csi/csi.py template` | Always |
| `SKILL.md` contains `python tools/csi/csi.py observe` | Always |
| `crowd-scan-example.md` contains `Convert Findings to CSI Evidence CSV` | Always |
| `tools/csi/README.md` contains `From Evidence Harvest to Memory Flywheel` | Always |
| No doc presents the score as buy/sell/hold advice | Always |

---

## Automated Test Suite

```bash
python -m unittest discover -s tests
```

Expected: 59+ tests pass, 0 failures.

---

## Private Data Audit

Run from repo root after any build or edit:

```bash
grep -RniE \
  "Arron|Carter|PCS|UTMA|MSFT|NVDA|VST|NKE|TSLA|\
Sep 2026|September 2026|July 2026|cost basis|current holdings|\
account value|liquidity deadline|buy now|sell now|hold this|\
high-conviction buy|best stock|guaranteed|alpha|beats the market|\
signal service|paid Discord|paid newsletter|sponsored|affiliate|\
investment advice|financial advisor|official government|\
State Department|Foreign Service|buy score|trade score|\
alpha score|expected return score|this stock scores|\
crowd is right|expected return is|fair value is|\
should rise|price target" \
  --include="*.py" --include="*.md" --include="*.csv" --include="*.txt" \
  --exclude-dir=".git" .
```

```bash
find . -name "*local*" -o -name ".env*" -o -path "./private/*" | grep -v ".git"
```

No private files should appear.

---

## Test — v0.5 Operability Commands

Run these after any change to `validation.py`, `importer.py`, or `wizard.py`.

```bash
# Validate sample evidence
python tools/csi/csi.py validate tools/csi/sample_evidence.csv

# Import sample markdown evidence
python tools/csi/csi.py import-md tools/csi/sample_evidence.md --output /tmp/csi_imported.csv

# Wizard dry-run (non-interactive)
python tools/csi/csi.py wizard --theme "Fictional AI infrastructure signal" --dry-run
```

### Manual wizard test (interactive)

```bash
python tools/csi/csi.py wizard
```

Follow the prompts. Verify:
- Banner includes non-advisory boundary
- Queries are generated
- Template creation is offered
- Validation runs before scoring
- Observation save is offered
- Next-steps commands are printed

---

## Test — xAI Harvest Adapter (Optional Module)

Run these after any change to `tools/csi/xai_harvest.py` or `tools/csi/csi.py` harvest-xai/oneclick commands.

### Automated Tests (All Mocked — No Real API Calls)

```bash
python -m pytest tests/test_csi_xai_harvest.py -v
```

Expected: 22 tests pass, 0 failures. All tests use mocks; no network requests made.

### Manual Tests (Requires XAI_API_KEY — Skip in CI)

These tests call the real xAI API. Only run if you have an API key and want to verify live behavior.

```bash
# Set your API key
export XAI_API_KEY="xai_..."

# Basic harvest (saves to evidence/csi/{slug}-xai-evidence.md)
python tools/csi/csi.py harvest-xai "fictional test theme"

# Full pipeline (harvest → import → validate → score → report → observe)
python tools/csi/csi.py harvest-xai "fictional test theme" --auto-score

# Check costs
cat data/csi/xai_costs.jsonl | jq .

# Check raw response
cat harvests/xai/*.json | jq . | head -50
```

### Harvest Adapter Verification Checklist

| Check | Expected |
|---|---|
| Missing `XAI_API_KEY` shows helpful message, no request sent | Always |
| Harvest prompt includes all 14 CSI columns | Always |
| Harvest prompt distinguishes X virality from evidence quality | Always |
| Harvest prompt prohibits buy/sell/hold advice | Always |
| Tool selection (x, web, x,web) maps correctly to request | Always |
| Cost conversion formula: ticks / 10_000_000_000 = USD | Always |
| Raw response JSON does NOT contain API key | Always |
| Markdown table extracted and saved to evidence.md | Always |
| `--auto-score` runs full pipeline (import → validate → score → report → observe) | Always |
| Validation failure stops auto-score and prints error | Always |
| HTTP 401 returns "Authentication failed" message | Always |
| HTTP 429 returns "Rate limited" message | Always |
| No output suggests buying, selling, or holding specific securities | Always |

### Cost Tracking

After harvest:

```bash
# Review cost log
cat data/csi/xai_costs.jsonl | jq '.'

# Verify structure
cat data/csi/xai_costs.jsonl | jq '.[] | keys' | head
```

Each entry should have: `created_at`, `theme`, `model`, `tools`, `cost_usd`, `raw_response_path`, `evidence_md_path`.

---

## Automated Test Suite

```bash
python -m unittest discover -s tests
python -m pytest tests/ -v
```

Expected: 156+ tests pass (134 original + 22 xAI harvest), 0 failures.

---

## When to Run Tests

| Event | Tests to run |
|---|---|
| Edit `SKILL.md` | Manual skill tests (evaluation-tests.md) |
| Edit `csi.py` | Automated + manual CLI smoke tests |
| Edit `validation.py` / `importer.py` / `wizard.py` | v0.5 operability tests |
| Edit `xai_harvest.py` or harvest-xai command | Automated xAI harvest tests (all mocked) |
| Edit scoring constants | Automated tests + verify score range |
| Edit sample_evidence.csv or .md | Import + report smoke test + private data audit |
| Before commit | Full automated suite + private data audit |
| Before PR | All of the above + xAI harvest tests |
