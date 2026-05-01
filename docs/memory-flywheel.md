# Memory Flywheel

Score signal → Save observation → Track outcome → Monthly review →
Suggested playbook updates → Better future crowd-signal assessment.

This system learns which crowd-signal patterns were useful.

**It does not learn which stocks to buy.**

---

## Crowd Signal Playbook ≠ Investment Playbook

The playbook must never suggest purchases, investments, trades,
position sizing, or buy/sell/hold actions.

It may only suggest improvements to crowd-signal assessment:

- source weighting,
- evidence requirements,
- scoring penalties,
- source coverage grading,
- trajectory classification,
- dissent requirements,
- echo-chamber detection,
- and monthly review methodology.

---

## What Gets Stored

**Observations** (`data/csi/observations.jsonl`):

One JSON record per scored evidence CSV. Fields:

- `signal_id` — stable slug (YYYY-MM-DD-theme)
- `created_at` — UTC timestamp
- `theme` — market theme
- `crowd_signal_quality_score` — 0–100
- `confidence` — standard / provisional / no-evidence
- `source_coverage_grade` — A / B / C / D / F
- `signal_trajectory` — emerging / accelerating / mainstreaming / saturated / fading / unknown
- `echo_chamber_risk` — true / false
- `source_classes` — list of source classes present
- `source_group_coverage` — group-level presence map
- `classification` — analysis-ready / monitor / reject
- `report_path` — path to saved markdown report
- `evidence_path` — path to input evidence CSV

**Outcomes** (`data/csi/outcomes.jsonl`):

One JSON record per reviewed observation. Fields:

- `signal_id` — links to observation
- `reviewed_at` — UTC timestamp
- `event_confirmed` — was the catalyst event real?
- `narrative_mainstreamed` — did the crowd narrative enter mainstream coverage?
- `trajectory_correct` — was the trajectory classification correct?
- `catalyst_occurred` — did the catalyst happen?
- `transmission_confirmed` — yes / partial / no / unknown
- `signal_usefulness` — useful / mixed / not_useful / unknown
- `failure_mode` — how did the signal fail (if it did)?
- `notes` — free text

**What outcome fields are NOT stored:**

- return, profit, loss
- buy_price, sell_price
- position_size, portfolio_allocation
- recommended_action

---

## What Counts as Effectiveness

A signal is effective if it:

- identified a real narrative, catalyst, or market-transmission mechanism,
- had a trajectory that proved directionally correct,
- had evidence that proved mechanistically sound,
- provided useful input for further thesis or risk analysis.

A signal is **not** measured by whether a stock went up.

---

## Signal Classification

New outputs use `analysis-ready / monitor / reject` (not `tradeable / watchlist`).

| Classification | Meaning |
|---|---|
| analysis-ready | Signal is sufficiently sourced and coherent to justify separate thesis, valuation, entry, and risk review. Not a buy/sell/hold recommendation. |
| monitor | Signal is interesting but incomplete, source-limited, too early, too crowded, or missing key evidence. |
| reject | Signal lacks sufficient independent evidence, specificity, mechanism, or source coverage, or is dominated by hype/echo-chamber risk. |

---

## Outcome Review Fields

| Field | Values | What it measures |
|---|---|---|
| event_confirmed | true/false/unknown | Was the catalyst event real? |
| narrative_mainstreamed | true/false/unknown | Did the narrative enter mainstream coverage? |
| trajectory_correct | true/false/unknown | Was trajectory classification directionally correct? |
| catalyst_occurred | true/false/unknown | Did the named catalyst happen? |
| transmission_confirmed | yes/partial/no/unknown | Did the market transmission mechanism play out? |
| signal_usefulness | useful/mixed/not_useful/unknown | Overall signal quality in hindsight |
| failure_mode | see list | How did the signal fail? |

**Failure modes:**

```
none                  signal did not fail
single_source         all evidence came from one source
hype                  hype dominated, real evidence was thin
priced_in             narrative was already fully priced at time of scoring
wrong_transmission    mechanism didn't play out as claimed
no_catalyst           the named catalyst did not occur
trajectory_wrong      trajectory classification was incorrect
other                 other failure
```

---

## Monthly Review

The `monthly-review` command generates a markdown effectiveness review for a given month.

What it computes:

- signals scored and reviewed
- useful / mixed / not_useful / unknown counts
- average score for the period
- source-class usefulness breakdown
- trajectory accuracy rate
- narrative mainstreaming rate
- event confirmation rate
- failure mode counts
- signals to continue monitoring
- signals to retire
- suggested playbook updates (human approval required)

**Note:** If there are no reviewed outcomes, the review generates a useful empty-state report.
It does not invent lessons from no data.

---

## Playbook Updates

The `playbook` command generates a local crowd-signal playbook from all accumulated data.

**Minimum thresholds:**

- 5 reviewed signals → tentative lessons
- 20 reviewed signals → stronger patterns

The playbook contains:

- current best signal patterns (useful observations)
- signal patterns that failed
- source-class usefulness table
- trajectory accuracy table
- penalty lessons (from failure mode patterns)
- scoring adjustments to consider
- evidence requirements to strengthen

---

## Human Approval Rule

Suggested playbook updates are not automatically applied.

All scoring changes to `csi.py` require human review and manual editing.

The tool suggests. The human decides.

---

## Data Privacy

Generated data files are gitignored:

```
data/csi/*.jsonl
reports/csi/*.md
reviews/csi/*.md
playbooks/crowd-signal-playbook.md
```

Do not commit personal observations, outcomes, or playbooks to the public repo.
Evidence CSVs should use fictional tickers and themes for any shared examples.

---

## Non-Advisory Boundary

This system evaluates crowd-signal usefulness.
It does not recommend purchases, investments, trades, position sizing,
or buy/sell/hold actions for any security.
