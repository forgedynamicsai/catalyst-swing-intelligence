# Known Gaps

Catalyst Swing Intelligence is intentionally conservative about these gaps.
When source coverage is incomplete, the system labels outputs `source-limited`
rather than invent confidence.

These are known limitations, not failures. Each gap is documented with its
current state, why it matters, and planned direction.

---

## Gap 1 — No Built-In Web Search Runner Yet

### Current state

The system generates search queries, evidence-harvest plans, and CSI evidence
schemas. It does not yet automatically search the open web.

Users or their LLM/runtime must currently perform searches manually or through
their agent's search/browser tools.

### Why this matters

The system is search-first and low-cost, but evidence acquisition still depends
on the user or agent runtime. A new user without an agent setup must copy queries
into a browser manually.

### Planned direction

Add an optional search runner or search-handoff workflow that can collect public
source URLs and snippets without requiring paid APIs.

This will not include:

- scraping behind logins or paywalls,
- credentialed data sources,
- brokerage or financial data APIs,
- guaranteed coverage of any market or theme.

See `docs/roadmap.md` — v0.6.

---

## Gap 2 — No Local Dashboard Yet

### Current state

The system produces markdown reports, local JSONL observations/outcomes, monthly
reviews, and crowd-signal playbooks. It does not yet provide a visual dashboard.

### Why this matters

Markdown is portable and low-cost, but users with many observations may want a
clearer way to browse signals, outcomes, source classes, and playbook changes over
time.

### Planned direction

Add a static HTML dashboard that renders local reports, observations, monthly
reviews, and playbook summaries.

This will:

- remain local-first,
- avoid required external services,
- not add live data feeds or market prices,
- not provide investment recommendations.

See `docs/roadmap.md` — v0.7.

---

## Gap 3 — No Large-Scale Real-World Calibration Yet

### Current state

The scoring model is deterministic and documented. The weights and penalties have
not yet been calibrated against a large set of historical observations.

### Why this matters

The current score is useful for consistency and research discipline, but its
predictive usefulness for identifying durable crowd-signal patterns must be learned
over time through the memory flywheel.

### Planned direction

Use the memory flywheel — `observe`, `outcome`, `monthly-review`, `playbook` — to
compare scored observations against later outcomes, then refine source-class
lessons, penalty guidance, trajectory classification, and playbook rules.

This will not claim:

- market-beating performance,
- alpha generation,
- investment prediction accuracy,
- guaranteed signal quality.

See `docs/roadmap.md` — v0.8.

---

## Non-Advisory Boundary

These gaps are about improving crowd-signal assessment methodology.
Closing them will not turn this system into an investment recommendation engine.

This roadmap improves crowd-signal assessment, not investment recommendations.
