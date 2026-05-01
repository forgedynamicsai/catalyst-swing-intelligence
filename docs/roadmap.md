# Roadmap

This roadmap improves crowd-signal assessment, not investment recommendations.

Each version improves operability, coverage, or calibration of the
crowd-signal intelligence workflow. No version will add:

- buy/sell/hold recommendations,
- price targets or expected returns,
- guaranteed signal quality or market-beating performance,
- investment advice of any kind.

See `docs/known-gaps.md` for the current known limitations behind each item.

---

## Shipped

### v0.1–v0.2 — Public Skill and Scoring Model

- Public skill (`SKILL.md`) with 11 modes
- 100-point Crowd Signal Quality Score model
- Signal trajectory classification
- Signal Fit Classification: `analysis-ready / monitor / reject`
- Legal/regulatory checklist and contributor evaluation checklist
- Evaluation tests

### v0.3 — Reference Implementation

- Deterministic CLI scoring (`tools/csi/`)
- Search query generator
- Evidence CSV template
- Markdown report generation
- Standard library only, zero paid APIs

### v0.4 — Memory Flywheel

- `observe` — save scored signal as local observation
- `outcome` — attach crowd-signal effectiveness review
- `monthly-review` — monthly crowd-signal effectiveness report
- `playbook` — generate crowd-signal playbook from accumulated data
- Local JSONL + markdown storage, gitignored

### v0.4.1 — Vocabulary Alignment

- Replaced `tradeable / watchlist / reject` with `analysis-ready / monitor / reject`
- Definitions consistent across all public files

### v0.4.1 — Evidence Harvest Bridge

- SKILL.md output contract bridges directly to CLI commands
- Example CSV mapping in crowd-scan example

### v0.5 — Guided Terminal Workflow

- `wizard` — guided step-by-step workflow with `--dry-run`
- `validate` — pre-flight policy gate (schema, ranges, source class, advisory language)
- `import-md` — convert LLM-produced markdown tables to CSI evidence CSV
- 93 automated tests passing

---

## Planned

### v0.6 — Optional Search Runner / Search Handoff

**Goal:** reduce the manual step between query generation and evidence CSV population.

Planned:

- Generate search-ready URLs from query output
- Accept agent-collected source snippets as structured input
- Optionally fetch user-provided public URLs (no login, no paywall)
- Preserve search-first, zero-paid-API design

Not included:

- scraping behind logins or paywalls,
- brokerage data feeds,
- guaranteed market coverage.

---

### v0.7 — Static HTML Dashboard

**Goal:** make it easier to browse accumulated observations, outcomes, and playbook evolution without reading raw markdown.

Planned:

- Render local observations table
- Render monthly review summaries
- Render source-class usefulness charts
- Render playbook evolution log
- Local-first, no external service required
- No live data feeds, no market prices

Not included:

- investment recommendations,
- price displays,
- trading signals.

---

### v0.8 — Calibration and Playbook Refinement

**Goal:** use accumulated memory flywheel data to improve scoring weight guidance and playbook rules.

Planned:

- Analyze accumulated observations and outcomes
- Compare source coverage grades to usefulness
- Compare trajectory classifications to later outcome reviews
- Suggest scoring adjustments and playbook refinements
- Require human approval before any scoring weight changes

Not included:

- automatic scoring weight changes,
- market-beating performance claims,
- investment prediction accuracy claims.

---

## Non-Advisory Boundary

Catalyst Swing Intelligence is intentionally conservative about these gaps.
When source coverage is incomplete, the system labels outputs `source-limited`
rather than invent confidence.

This roadmap improves crowd-signal assessment, not investment recommendations.
