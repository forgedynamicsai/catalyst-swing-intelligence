---
name: swing-intelligence
description: >
  Catalyst-driven swing trading intelligence for U.S. equities and ETFs.
  Handles the full workflow: macro regime check → crowd signal analysis →
  thesis construction → entry discipline → concentration risk → earnings gate
  → behavioral guardrails → long-horizon account governance → exit planning.
  Use when building a new swing position, analyzing crowd signals from X or
  Reddit, reviewing a position before earnings, managing concentration risk,
  constructing a next-cycle portfolio, or planning exits toward a hard
  liquidity deadline. Does NOT cover business red-teaming, AI architecture
  reviews, SaaS metrics, debt payoff, or federal resumes.
triggers:
  - swing trade
  - next cycle
  - crowd signal
  - wisdom of the crowd
  - what is the crowd saying
  - earnings gate
  - should I hold through earnings
  - entry zones
  - add-more zones
  - position too large
  - concentration risk
  - build next portfolio
  - deploy cash after trim
  - X thread
  - publish this thesis
  - long horizon account
  - custodial account
  - regret minimizer
  - what if I sell and it skyrockets
  - thesis broken
  - beaten down check
  - macro regime
  - geopolitical catalyst
  - war trade
  - sanctions trade
  - tariffs
  - critical minerals
  - hard liquidity deadline
  - exit by deadline
  - staged exit
tools:
  - web-search
  - finance-data
  - calculator
mutating: false
---

# Swing Intelligence

Companion skills: `staged-position-entry` (entry discipline and tranche sizing),
`thesis-break-protocol` (exit rules when thesis fails). This skill covers everything
between "what should I trade" and "when do I exit." The companion skills govern
the mechanics of entry and the mechanics of exit.

See `PERSONALIZATION.local.md` for your specific accounts, deadlines, watchlists,
and personal rules. If that file does not exist, copy `PERSONALIZATION.example.md`
and fill it in before using the child-account or liquidation-plan modes.

---

## Master Operating Rule

```
For long-horizon accounts, compound.
For swing accounts, trade the plan.
Never apply short-term swing logic to long-term capital.

Do not confuse a correct thesis with a good entry.
Do not confuse a good company with a good swing trade.
Do not confuse ticker diversification with factor diversification.
Do not let one earnings print control the whole account.
Trim when concentration becomes the risk.
Hold cash until price enters the zone.
```

---

## When to use

- Building a new swing trade from scratch
- Evaluating a crowd signal from X, Reddit, or financial media
- Reviewing a position 1–5 days before earnings
- A single position exceeds 30% of the swing account
- Constructing a next-cycle portfolio after a trim or catalyst clear
- Mapping geopolitical events to investable market exposure
- Planning staged exits toward a hard liquidity deadline
- Publishing a trade thesis as a compliant social experiment
- Reviewing a long-horizon custodial account separately from the swing account
- Evaluating a long-horizon turnaround or moonshot allocation

## When NOT to use

- Entry discipline and tranche sizing → `staged-position-entry`
- Thesis-broken exit decisions → `thesis-break-protocol`
- Business plan red-teaming → `wroughtai-business-red-team`
- AI architecture review → `ai-product-architecture-red-team`
- SaaS metrics pipeline → `deterministic-saas-metrics-cfo`
- Debt payoff planning → `debt-avalanche-liquidity-planner`
- Federal resume writing → `federal-resume-generation`
- Day trading or options — out of scope

---

## Mode: `macro-first`

**Use before building any new swing cycle. Prevents ticker-chasing.**

### Core questions
1. Is the market rewarding growth, value, defensives, energy, small caps, or international?
2. Is AI/tech still leading, or is leadership rotating?
3. Are rates helping or hurting long-duration growth names?
4. Are geopolitical risks concentrated in the current portfolio?
5. Are previous winners still early, or is this buying someone else's exit?

### Workflow
1. Check current sector leadership (e.g., QQQ/SMH/XLK relative strength).
2. Check rates and Fed expectations.
3. Check geopolitical catalysts: export controls, tariffs, energy security, sovereign risk.
4. Classify regime.

| Regime | Portfolio bias |
|---|---|
| AI risk-on | AI infrastructure, semis, cloud, power |
| Rotation | Utilities, energy, financials, healthcare |
| Risk-off | Cash, dividend ballast, fewer earnings holds |
| Rate shock | Reduce high-multiple growth |
| Geopolitical shock | Reduce concentrated geopolitical exposure |

### Output
```markdown
## Macro Regime
- Current regime:
- Leadership:
- Rate backdrop:
- Geopolitical risk:
- Implication for next cycle:

## Portfolio Instruction
- Lean in:
- Reduce:
- Avoid:
```

---

## Mode: `crowd-scan`

**Use when a crowd narrative emerges from X, Reddit, or financial media.**

This mode scores the quality of the crowd signal — not the attractiveness of
any security. See `docs/crowd-signal-scoring.md` for the full model.

```
Crowd Signal Quality  ≠  Security Risk  ≠  Trade Decision
```

### Sourcing rule
Every output must declare exact sources (X/finTwit, Reddit, specific accounts)
and evidence quality. Never present crowd opinion as personal analysis. Always
frame output as "crowd signal assessment, not financial advice." Offer to pull
raw posts for verification.

### Crowd Signal Quality Score — 100-point model

**Base components (max 100):**

| Component | Weight | What it measures |
|---|---:|---|
| Signal volume | 15 | How much discussion exists |
| Source independence | 20 | Whether sources are unrelated or echoing each other |
| Specificity | 20 | Whether the crowd names a causal mechanism, not just a ticker |
| Evidence quality | 20 | Whether claims cite filings, transcripts, data, or primary sources |
| Time acceleration | 10 | Whether attention is increasing over the relevant window |
| Catalyst alignment | 10 | Whether the signal maps to a dated or identifiable catalyst |
| Dissent quality | 5 | Whether credible opposing views are acknowledged |

**Penalties (applied after base score):**

| Penalty | Max deduction | Why |
|---|---:|---|
| Meme/hype penalty | −15 | High emotion, low mechanism |
| Crowding penalty | −15 | Narrative already widely known |
| Price-moved penalty | −20 | Signal may already be priced in |
| Single-source penalty | −20 | Echo chamber risk |
| Loose ticker-basket penalty | −10 | Weak earnings transmission |

Score interpretation: 75–100 = high quality · 50–74 = moderate · 25–49 = weak · 0–24 = noise.

**The Crowd Signal Quality Score is not a buy score, sell score, risk rating, or
expected-return score. A high score means the signal is well-evidenced — it does
not mean the security is safe, cheap, or likely to rise.**

### Signal trajectory
Classify the crowd signal lifecycle as one of:

| Trajectory | Meaning |
|---|---|
| Emerging | Low volume, high specificity, early signal |
| Accelerating | Independent mentions increasing |
| Mainstreaming | Financial media and generalist accounts picking it up |
| Saturated | Widely known, likely crowded |
| Fading | Repeated old claims, fewer new sources |

Trajectory describes the signal lifecycle only — not price direction, expected
return, fair value, or any prediction about the underlying security.

### Workflow
1. Declare source universe.
2. Tag signals against the catalyst taxonomy.
3. Score base components and apply penalties.
4. Classify signal trajectory.
5. Separate mechanism from tickers.
6. Confirm market transmission is direct, not loose.
7. Apply priced-in filter.
8. Map dissent — credible opposing views.
9. Rank 1–3 cleanest expressions; explicitly reject loose baskets.
10. Classify trade fit: `tradeable`, `watchlist`, or `reject`.

### Catalyst taxonomy tags
Rates · Inflation · Earnings · Regulation · Fiscal policy · Energy · AI infrastructure ·
Geopolitics · Supply chain · ETF flows · Crypto · Sovereign debt · Election risk ·
Cyber · Resource nationalism · Critical minerals · Defense spending · Healthcare policy

### Output
```markdown
## Crowd Signal Assessment

- Theme:
- Source universe: [X/finTwit | Reddit | Financial media — name accounts if available]
- Core crowd claim:
- Mechanism:
- Signal trajectory: [emerging | accelerating | mainstreaming | saturated | fading]
- Crowd Signal Quality Score: __/100
- Penalties applied:
  - Meme/hype: [−X or none]
  - Crowding: [−X or none]
  - Price-moved: [−X or none]
  - Single-source: [−X or none]
  - Loose ticker basket: [−X or none]
- Evidence quality: [filing | transcript | analyst note | channel check | rumor | meme-only]
- Source independence: [independent | partially echoed | single-source echo]
- Dissent quality: [credible dissent exists | weak dissent | no dissent found]
- Priced-in risk: [not priced | partially priced | likely priced in]

## Market Transmission

- Earnings impact:
- Margin impact:
- Supply/demand impact:
- Policy/regulatory impact:
- Multiple/risk-premium impact:
- Catalyst timing:

## Trade Fit Classification

- Classification: [tradeable | watchlist | reject]
- Why:
- What separate analysis is still required:
- Not a buy/sell/hold recommendation.

## Rejected / Too Loose

-
```

---

## Mode: `thesis-build`

**Use when constructing a new catalyst-driven swing trade.**

For entry mechanics (tranche sizing, add-more zones, blended cost basis, dry powder
rules), run `staged-position-entry` after defining the thesis here.

### Required contract — all fields required, no exceptions

1. **Ticker / ETF**
2. **Primary catalyst** — specific, dated event
3. **Secondary catalysts**
4. **Entry zone** — price range, not "wait for a pullback"
5. **Add-more zone** — defined before entry, not during
6. **Hard stop**
7. **Target price / exit logic**
8. **Catalyst calendar** — earnings, FOMC, CPI, policy votes, product launches
9. **Position size** — % of swing account
10. **Risk/reward ratio**
11. **Thesis-broken conditions** — specific mechanism, not generic risk
12. **Exit deadline** — hard date or catalyst event

### Thesis-broken specificity rule
Never accept generic risks like "market volatility" or "macro headwinds."
Every thesis must name the specific failure mode that would force an exit:
- The exact metric that, if it disappoints, breaks the earnings transmission
- The guidance statement that would contradict the catalyst timing
- The macro regime shift that removes the mechanism
- The crowding signal that means the trade is consensus before the catalyst fires

### Entry quality scoring

| Score | Meaning | Action |
|---:|---|---|
| 1–2 | Chasing / extended | Do not enter |
| 3–4 | Good company, bad entry | Wait |
| 5–6 | Fair entry | Starter tranche only |
| 7–8 | Attractive pullback | Enter with planned size |
| 9–10 | Washed-out, thesis intact | Full tranche, define add-more zones |

Workflow: compare to prior high/low → compare to predefined entry zone → check
valuation → confirm catalyst is ahead, not passed → classify entry quality.

### Output
```markdown
## Thesis
- Ticker:
- Primary catalyst:
- Catalyst date:
- Mechanism:
- Entry zone:
- Add-more zone:
- Hard stop:
- Target / exit logic:
- Catalyst calendar:
- Position size:
- Risk/reward:
- Thesis-broken conditions:
- Exit deadline:
- Entry quality score: /10
- Entry action: [enter now | starter only | wait | avoid]
```

---

## Mode: `concentration-check`

**Use when a single position exceeds 30% of the swing account, or before earnings.**

| Position weight | Status |
|---:|---|
| 0–20% | Normal |
| 20–30% | Concentrated but acceptable |
| 30–40% | High conviction only — justify explicitly |
| 40–50% | Needs explicit written justification |
| 50%+ | Account-level risk |
| 60%+ | Trim unless deliberately accepting major drawdown |

### Workflow
1. Calculate current position weight as % of account.
2. Calculate P&L impact of ±5%, ±8%, ±10% moves.
3. Compare upside regret vs. downside protection.
4. Recommend trim size: 0, small (3–5 shares or 10%), medium (25%), or half.
5. Define post-event action (hold core, exit fully, add on dip).

### Output
```markdown
## Concentration Review
- Position:
- Current weight:
- Event risk:
- +10% impact on account: +$__
- -10% impact on account: -$__

## Recommendation
- Trim: [amount / %]
- Hold: [Y/N]
- Reason:
- Post-event action:
```

---

## Mode: `earnings-gate`

**Use 1–5 trading days before any major earnings catalyst.**

For thesis-broken exit logic after earnings, use `thesis-break-protocol`.

### Required inputs
Current price · Cost basis · Unrealized gain/loss · Position size · Earnings date ·
Thesis status · Market expectations · Peer read-throughs · Downside gap risk

### Decision tree
```
IF position is >40% of account:
    Trim before earnings unless thesis is exceptional and downside is accepted.

IF unrealized gain is >10% and catalyst is binary:
    Consider trimming 25–50%.

IF position has no profit cushion:
    Do not add before earnings.

IF thesis is intact but position is oversized:
    Trim partial, hold core.

IF thesis is broken before earnings:
    Exit. Do not wait for the report.
```

### Output
```markdown
## Earnings Gate
- Ticker:
- Earnings date:
- Position size / weight:
- Profit cushion:
- Thesis status: [intact | weakening | broken]
- Bull case:
- Bear case:
- Key metrics to watch:
- Guidance threshold that would confirm thesis:
- Guidance threshold that would break thesis:
- Risk/reward at current size:

## Action
- Hold: [Y/N — amount]
- Trim: [Y/N — amount]
- Exit: [Y/N]
- Add: [Y/N — only if no-profit-cushion rule allows]

## Post-Earnings Action Plan
- If beats + guides up:
- If beats + guides flat:
- If misses or guides down:
- Thesis-broken trigger:
```

---

## Mode: `geopolitical-catalyst`

**Use for war, sanctions, tariffs, export controls, energy shocks, critical minerals,
China/Taiwan risk, Middle East escalation, cyberwarfare, or sovereign debt crises.**

### Event classification
War · Sanctions · Tariffs · Export controls · Resource nationalism ·
Energy route disruption · Cyberwarfare · Sovereign crisis · Election risk ·
Critical minerals shock · Defense spending acceleration

### Required contract — all fields required

1. Event + actors
2. Escalation path
3. De-escalation path
4. Transmission mechanism (earnings / supply / demand / margins / risk premium / capital flows)
5. Direct beneficiaries — tickers/ETFs
6. Direct losers — tickers/ETFs
7. Second-order beneficiaries
8. Commodity exposure
9. Duration of catalyst (days / weeks / months / structural)
10. Crowdedness — how many funds already own the obvious trade
11. Tail risk — what makes this worse than expected
12. Repricing test — is this already in the price?

---

## Mode: `next-cycle`

**Use after trimming winners or after a catalyst clears.**

### Constraints
- 3–5 names maximum
- Daily/weekly timeframes; no day trading
- Must be liquidatable by the deadline in `PERSONALIZATION.local.md`
- No position above 40% of account without explicit written justification
- Staged entries only — full position at once is a discipline violation
- Keep cash reserve for better prices and unexpected opportunity

### Workflow
1. Calculate account value and available cash.
2. Map current exposure by theme (avoid doubling a theme already represented).
3. Run `macro-first` to confirm regime before screening.
4. Select 3–5 candidates that pass entry quality scoring (score ≥ 6).
5. Assign target allocation.
6. Define entry zones, add-more zones, and exit triggers.
7. Confirm all positions are liquidatable by the hard deadline.

### Output
```markdown
## Next Cycle Portfolio
| Ticker | Role | Target Weight | Entry Zone | Add-More Zone | Exit Trigger | Liquidatable by deadline? |
|---|---|---|---|---|---|---|

## Cash Plan
- Deploy now:
- Hold in reserve:
- Trigger for deployment:
- Hard deadline for full exit:
```

---

## Mode: `regret-check`

**Invoke when FOMO, regret, or second-guessing a trim is present.**

Trigger phrases: "What if I sell and it skyrockets?", "Should I chase now?",
"What if I miss the move?", "Claude says hold."

### Workflow
1. Frame the real decision (risk control vs. prediction).
2. Quantify missed upside if the trim was wrong.
3. Quantify avoided downside if the trim was right.
4. Name the remaining exposure after the trim.
5. Offer the compromise position.

Key principle: Trimming a concentrated position does not abandon the thesis.
It converts account-level risk into a controlled core position. If the stock
skyrockets, the account still has exposure. The decision was about concentration
control, not prediction.

### Output
```markdown
## Regret Analysis
- Fear:
- Missed upside if wrong:
- Avoided downside if right:
- Remaining exposure after trim:
- Best compromise:

## Decision
```

---

## Mode: `publish-signal`

**Use when publishing a crowd signal thesis as a compliant X/social post.**

### Non-negotiable disclaimer requirements
Every published post must include all of the following:
- "Not financial advice"
- "Not a solicitation to buy or sell"
- "DYOR / do your own research"
- "I may or may not hold positions"
- "This is an experiment, not a recommendation"

### X thread format
```
1/3 — Core thesis + mechanism (max 280 characters)
2/3 — Evidence quality + timing window + 2–3 tickers (max 280 characters)
3/3 — DYOR disclaimer + engagement CTA + 2–3 hashtags (max 280 characters)
```

Bold key terms. Invite replies and disagreement, not followers or trades.
Purpose is information-sharing and crowd validation, not promotion.

---

## Mode: `long-horizon-account`

**Use for long-horizon custodial or investment accounts (UTMA, 529, Roth IRA, etc.)
with a 5–15 year time horizon. Never apply swing-trading logic here.**

See `PERSONALIZATION.local.md` for your specific account names, beneficiaries,
target years, and current holdings. If no personalization file exists, use
these generic guidelines.

### Core principle
Long-horizon accounts compound. They do not swing.
Short-term swing logic applied to long-horizon capital is a category error.

### Generic allocation framework

| Category | Target range |
|---|---:|
| Core broad-market ETFs | 50–65% |
| Mega-cap compounders | 25–40% |
| Turnaround / moonshot bets | 5–15% |
| Cash | Minimal |

### Turnaround bet assessment
Add to a beaten-down brand or turnaround position only when:
- Two consecutive quarters of positive revenue growth (demand stabilizing)
- Gross margin stops falling (promotional pressure easing)
- Primary competitive pressure visibly easing
- Key geography or product line stabilizing

Until those signals appear: hold small, do not add, do not exit.

### Moonshot / public venture bet assessment
Treat high-volatility speculative positions as call options on future business
models not yet proven. Size them accordingly (5–10% max).

Add only when:
- Regulatory approval achieved for the core optionality (not "expected soon")
- Visible commercial revenue from the speculative thesis (not projections)
- Core business margins stabilizing
- Price falls while execution evidence improves (better asymmetry, not averaging down)

### Output
```markdown
## Long-Horizon Account Review
- Account name:
- Beneficiary:
- Time horizon:
- Current risk level:
- Core allocation:
- Speculative allocation:
- Action today:
- What not to do:
```

---

## Mode: `liquidation-plan`

**Use when positions must be closed before a hard deadline (relocation, liquidity
requirement, major life event, or fixed date). Prevents a good trade from
becoming a logistics problem.**

### Required contract

1. Current holdings with basis and unrealized P&L
2. Cash balance
3. Required full liquidity date
4. Catalyst dates between now and liquidation
5. Trim schedule (progressive, not all-at-once)
6. Full exit schedule
7. Tax considerations if material (short-term vs. long-term gain)
8. Maximum drawdown tolerated before forced exit
9. "No new risk after [date]" rule — define it before you need it
10. Contingency if market is illiquid near deadline

### Hard rule
Define the no-new-risk date before deploying any new capital.
This date is not negotiable once set.

---

## Quality Checklist

Before delivering any output, verify:

- [ ] Thesis-broken conditions are specific, not generic
- [ ] Entry zone is a price range, not "wait for a pullback"
- [ ] Position size is stated as % of account
- [ ] Catalyst is dated, not vague ("Q3 earnings" not "upcoming catalyst")
- [ ] Exit condition is pre-written before the trade is entered
- [ ] Crowd signals declare source and include convergence score
- [ ] Published posts include all five required disclaimers
- [ ] Long-horizon account output contains no swing-trading logic
- [ ] Geopolitical output includes priced-in assessment
- [ ] Liquidation plan includes hard "no new risk after [date]" rule
- [ ] Concentration check runs before any position above 30% goes into earnings

---

## Skill Index

| Mode | Invoke when | Output artifact |
|---|---|---|
| `macro-first` | Before screening any names | Regime + portfolio instruction |
| `crowd-scan` | Crowd signal, social sentiment | Signal block + tradeable expression |
| `thesis-build` | Building swing trade, entry zones | Full thesis with 12 required fields |
| `concentration-check` | >30% in one position | Concentration review + trim rec |
| `earnings-gate` | 1–5 days before earnings | Decision tree + post-call plan |
| `geopolitical-catalyst` | War, sanctions, tariffs, export controls | Exposure map with 12 required fields |
| `next-cycle` | Deploy cash, new portfolio | Portfolio table + cash plan |
| `regret-check` | FOMO, "what if I sell" | Regret analysis + decision |
| `publish-signal` | X thread, social experiment | Compliant 3-part thread |
| `long-horizon-account` | Custodial / long-horizon account review | Account review block |
| `liquidation-plan` | Hard deadline, forced exit schedule | Staged exit schedule |
