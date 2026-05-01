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

## Automated Test Suite

```bash
python -m unittest discover -s tests
```

Expected: 53+ tests pass, 0 failures.

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

## When to Run Tests

| Event | Tests to run |
|---|---|
| Edit `SKILL.md` | Manual skill tests (evaluation-tests.md) |
| Edit `csi.py` | Automated + manual CLI smoke tests |
| Edit scoring constants | Automated tests + verify score range |
| Edit sample_evidence.csv | Report smoke test + private data audit |
| Before commit | Full automated suite + private data audit |
| Before PR | All of the above |
