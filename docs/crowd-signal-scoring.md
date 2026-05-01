# Crowd Signal Scoring

This project scores the quality of a crowd signal — not the attractiveness,
risk, or expected return of any security.

---

## Core Distinction

```
Crowd Signal Quality  ≠  Security Risk  ≠  Trade Decision
```

The score answers one question:

> "Is there independent, specific, evidence-backed convergence around a market
> narrative — or just noisy social-media enthusiasm?"

It does **not** answer:

- Should I buy this?
- Is this security safe?
- What is the expected return?
- What is the fair value?
- Will the crowd be right?

A high Crowd Signal Quality Score means the signal is more coherent and
better evidenced. It does not mean the security is cheap, safe, or likely to rise.

---

## Crowd Signal Quality Score — 100-Point Model

### Base Components

| Component | Weight | What it measures |
|---|---:|---|
| Signal volume | 15 | How much discussion exists across sources |
| Source independence | 20 | Whether sources are unrelated or merely echoing each other |
| Specificity | 20 | Whether the crowd names a causal mechanism, not just a ticker |
| Evidence quality | 20 | Whether claims cite filings, transcripts, data, expert analysis, or primary sources |
| Time acceleration | 10 | Whether attention is increasing over the relevant window |
| Catalyst alignment | 10 | Whether the signal maps to a dated or identifiable catalyst |
| Dissent quality | 5 | Whether credible opposing views exist and are honestly addressed |

Maximum base score: 100

### Penalties

| Penalty | Max deduction | Why |
|---|---:|---|
| Meme/hype penalty | −15 | High emotion, low mechanism — signal contains claims but not causes |
| Crowding penalty | −15 | The narrative is already widely known and likely priced in crowd behavior |
| Price-moved penalty | −20 | The underlying security has already moved significantly on this signal |
| Single-source penalty | −20 | Signal appears to originate from one account echoed by many |
| Loose ticker-basket penalty | −10 | Theme may be real but the tickers cited have weak earnings transmission |

Minimum adjusted score: 0. Penalties stack.

### Score Interpretation

| Adjusted score | Interpretation |
|---:|---|
| 75–100 | High-quality signal — strong evidence convergence, low echo-chamber risk |
| 50–74 | Moderate-quality signal — some independent evidence, mechanism partially specified |
| 25–49 | Weak signal — thin evidence, possible echo chamber, loose mechanism |
| 0–24 | Noise — meme-driven, single-source, or already fully priced |

> **Reminder:** Score thresholds do not trigger buy/sell/hold recommendations.
> A score of 80 means the signal is well-evidenced. Separate entry, valuation,
> risk, and catalyst analysis is still required before any capital decision.

---

## Signal Trajectory Classification

This classification estimates the lifecycle stage of the crowd signal — not any
prediction of price movement, expected return, fair value, or downside risk.

| Trajectory | Meaning |
|---|---|
| **Emerging** | Low volume, high specificity. Early signal from a small number of informed accounts. |
| **Accelerating** | Independent mentions increasing. Signal spreading beyond the original source cluster. |
| **Mainstreaming** | Financial media and generalist accounts are picking it up. Risk of crowding is rising. |
| **Saturated** | Widely known. Signal is likely crowded. Contrarian risk increases. |
| **Fading** | Fewer new sources. Repeated old claims dominate. Original catalyst may have passed or been priced. |

Trajectory is used only to describe where the crowd signal is in its lifecycle.

Do not use trajectory to forecast:
- price direction
- expected return
- fair value
- downside risk
- probability of trade success

---

## Three-Layer Architecture

The public skill separates crowd intelligence into three distinct layers.
These layers must not be collapsed into a single score.

### Layer 1 — Crowd Intelligence
- What is the crowd saying?
- Are sources independent?
- Is the mechanism specific or vague?
- Is evidence primary (filings, data, transcripts), analytical, rumor-based, or meme-only?
- Is the signal accelerating, mainstreaming, or fading?
- Are dissenting arguments credible?

### Layer 2 — Market Transmission
- How could the crowd signal affect earnings, margins, supply/demand, capex, regulation, multiples, or capital flows?
- Which sectors, industries, or broad instruments could be affected?
- What catalyst timing matters?

### Layer 3 — Signal Fit
- Is there a dated catalyst?
- Is the signal already priced in?
- Is entry discipline applicable?
- What would break the thesis?
- Should this be `analysis-ready`, `monitor`, or `reject`?

| Classification | Meaning |
|---|---|
| `analysis-ready` | Signal is sufficiently sourced and coherent to justify separate thesis, valuation, entry, and risk review. Not a buy/sell/hold recommendation. |
| `monitor` | Signal is interesting but incomplete, source-limited, too early, too crowded, or missing key evidence. |
| `reject` | Signal lacks sufficient independent evidence, specificity, mechanism, or source coverage, or is dominated by hype/echo-chamber risk. |

`Signal Fit` classification is not a buy/sell/hold recommendation.
It is a signal-routing decision that determines whether further analysis is warranted.

---

## Required Output Language

### Good

```
The crowd signal has a 74/100 evidence-convergence score.
The signal appears accelerating but not yet mainstreaming.
The mechanism is specific: supply disruption → spot price increase → margin expansion.
This still requires separate entry, valuation, risk, and thesis-broken analysis.
```

### Bad — do not write this

```
This stock has a 74/100 score.
This is a buy.
Expected return is elevated.
The crowd is right.
```

---

## What the Score Is Not

- Not a buy score
- Not a sell score
- Not a risk score
- Not an alpha score
- Not an expected-return score
- Not a prediction of crowd accuracy
- Not financial advice
