# Catalyst Swing Intelligence

A Claude Code skill for structuring catalyst-driven market research,
Wisdom-of-the-Crowds signal assessment, and swing-trade decision discipline.

---

## What This Is

A decision-support framework for:

- evaluating the quality, independence, specificity, and trajectory of crowd signals
- structuring catalyst-driven swing trade theses with required invalidation conditions
- managing concentration risk with explicit thresholds
- making pre-earnings decisions with pre-written action plans
- separating long-horizon capital from short-term swing accounts
- planning exits toward hard liquidity deadlines
- publishing crowd signal analyses with mandatory financial disclaimers

The core function is to evaluate **whether a crowd narrative is coherent and
well-evidenced** — not to tell users what to buy.

---

## What This Is Not

This is not a stock-picking bot, financial adviser, signal service, performance
guarantee, buy score, risk score, expected-return model, or personalized
investment recommendation.

The Crowd Signal Quality Score measures evidence convergence.
It does not measure expected return, security safety, or whether a user
should buy, sell, or hold anything.

See `DISCLAIMER.md` and `docs/legal-risk-release-checklist.md`.

---

## Who This Is For

- Retail investors who want structured decision discipline before deploying capital
- Traders who want pre-written exit and invalidation rules for every position
- Users who want to separate crowd signal quality from trade fit
- Anyone who wants to keep private portfolio context out of public skill logic

---

## Quick Start

```bash
# 1. Copy the skill into your Claude skills directory
cp -r skills/catalyst-swing-intelligence/ ~/.claude/skills/

# 2. Copy and fill in your private personalization
cp skills/catalyst-swing-intelligence/PERSONALIZATION.example.md \
   skills/catalyst-swing-intelligence/PERSONALIZATION.local.md

# 3. Edit PERSONALIZATION.local.md with your own accounts, risk limits, and rules
# 4. Never commit PERSONALIZATION.local.md
```

---

## Companion Skills

This skill works best alongside two companion skills (not included here):

- **`staged-position-entry`** — entry discipline, tranche sizing, blended cost basis, dry powder rules
- **`thesis-break-protocol`** — exit rules when a thesis fails, three-strike rule, rationalization checklist

---

## Which Mode Should I Use?

See [`docs/mode-decision-tree.md`](docs/mode-decision-tree.md).

| User intent | Mode |
|---|---|
| "What is the crowd saying?" | `crowd-scan` |
| "Build a trade thesis." | `thesis-build` |
| "Should I hold through earnings?" | `earnings-gate` |
| "One position is too large." | `concentration-check` |
| "What is the macro regime?" | `macro-first` |
| "I have cash after a trim." | `next-cycle` |
| "There is a geopolitical event." | `geopolitical-catalyst` |
| "I'm second-guessing a trim." | `regret-check` |
| "Write a compliant social post." | `publish-signal` |
| "This is a long-term account." | `long-horizon-account` |
| "I have a hard liquidity deadline." | `liquidation-plan` |

---

## How Crowd Signals Are Scored

See [`docs/crowd-signal-scoring.md`](docs/crowd-signal-scoring.md).

The **Crowd Signal Quality Score** (0–100) measures evidence convergence:

- Signal volume, source independence, specificity, evidence quality,
  time acceleration, catalyst alignment, and dissent quality
- Penalties for meme/hype, crowding, price-movement, single-source, and loose baskets
- Signal trajectory classification: Emerging → Accelerating → Mainstreaming → Saturated → Fading

```
Crowd Signal Quality  ≠  Security Risk  ≠  Trade Decision
```

A high score means the signal is well-evidenced. It does not mean you should buy.

---

## Public vs Private Files

This repository contains only public reusable methodology.

**Never commit:**

- current holdings or cost basis
- personal or family names
- account values or balances
- liquidity deadlines
- tax details
- personalized financial plans
- `PERSONALIZATION.local.md`

`PERSONALIZATION.local.md` is gitignored by default.
Use `PERSONALIZATION.example.md` as a template.

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md),
[`docs/contributor-evaluation-checklist.md`](docs/contributor-evaluation-checklist.md),
and [`docs/legal-risk-release-checklist.md`](docs/legal-risk-release-checklist.md).

---

## Reference Implementation

This repo includes a minimal search-first reference implementation under `tools/csi/`.

It does not require paid APIs.

It can generate search queries, create an evidence CSV template, score evidence
deterministically, and write a markdown crowd signal report.

Use it when you want a low-cost local workflow or a deterministic scoring helper
for the agent skill.

```bash
python tools/csi/csi.py queries "AI data center power scarcity"
python tools/csi/csi.py template --output evidence.csv
python tools/csi/csi.py score tools/csi/sample_evidence.csv
python tools/csi/csi.py report tools/csi/sample_evidence.csv --output report.md
python tools/csi/csi.py demo
```

See [`tools/csi/README.md`](tools/csi/README.md) and
[`docs/reference-implementation.md`](docs/reference-implementation.md).

---

## Memory Flywheel

The reference implementation can store scored crowd-signal observations locally,
attach later outcome reviews, generate monthly effectiveness reviews, and suggest
updates to a local crowd-signal playbook.

This helps evaluate which crowd-signal patterns were useful over time.

It does not evaluate whether the skill picked winning securities.

The crowd-signal playbook is not an investment playbook and must not suggest
purchases, investments, trades, position sizing, or buy/sell/hold actions.

```bash
python tools/csi/csi.py observe tools/csi/sample_evidence.csv --theme "AI infrastructure"
python tools/csi/csi.py list
python tools/csi/csi.py outcome SIGNAL_ID --usefulness useful --failure-mode none
python tools/csi/csi.py monthly-review --month 2026-05
python tools/csi/csi.py playbook
```

See [`docs/memory-flywheel.md`](docs/memory-flywheel.md).

---

## Evaluation Tests

See [`docs/evaluation-tests.md`](docs/evaluation-tests.md) for a manual test
suite to run after any change to `SKILL.md`.

See [`docs/testing-guide.md`](docs/testing-guide.md) for the automated test
suite for the reference implementation.

---

## Disclaimer

This is a decision-support framework, not financial advice.
See [`DISCLAIMER.md`](DISCLAIMER.md) for the full disclaimer.
