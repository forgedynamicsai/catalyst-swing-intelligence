# Catalyst Swing Intelligence

A public Claude Code skill for disciplined catalyst-driven swing-trade analysis.

This skill helps users structure:

- macro regime checks before deploying capital
- crowd-signal analysis with convergence scoring
- catalyst thesis construction with required contracts
- entry quality scoring and add-more zone planning
- concentration risk review with explicit thresholds
- earnings gate decisions with pre-written action plans
- thesis-broken conditions (specific, not generic)
- hard-deadline liquidation planning
- long-horizon account separation from swing capital
- compliant social publishing of trade theses

It does not tell users what to buy.

It forces better questions before capital is deployed.

---

## Companion Skills

This skill works best alongside:

- **`staged-position-entry`** — entry discipline, tranche sizing, blended cost basis, dry powder rules
- **`thesis-break-protocol`** — exit rules when a thesis fails, three-strike rule, rationalization checklist

---

## Installation

Copy `skills/catalyst-swing-intelligence/` into your Claude Code skills directory:

```bash
cp -r skills/catalyst-swing-intelligence/ ~/.claude/skills/
```

Then copy and fill in your personalization:

```bash
cp skills/catalyst-swing-intelligence/PERSONALIZATION.example.md \
   skills/catalyst-swing-intelligence/PERSONALIZATION.local.md
# Edit PERSONALIZATION.local.md with your accounts, deadlines, and rules
```

---

## Public vs Private Files

This repository contains only public reusable skill logic.

**Do not commit:**

- current holdings
- cost basis
- family names
- account values
- liquidity deadlines
- tax details
- personalized financial plans

Use `PERSONALIZATION.example.md` as a template. Keep your local version in
`PERSONALIZATION.local.md` — it is gitignored by default.

---

## Skill Modes

| Mode | Trigger | What it produces |
|---|---|---|
| `macro-first` | Before screening any names | Regime classification + portfolio instruction |
| `crowd-scan` | Crowd signal, social sentiment | Signal block with convergence score |
| `thesis-build` | Build swing trade | Full thesis with 12 required fields |
| `concentration-check` | >30% in one position | Review + trim recommendation |
| `earnings-gate` | 1–5 days before earnings | Decision tree + post-call action plan |
| `geopolitical-catalyst` | War, sanctions, tariffs, export controls | Exposure map |
| `next-cycle` | Deploy cash, new portfolio | Portfolio table + cash plan |
| `regret-check` | FOMO, "what if I sell" | Regret analysis + decision |
| `publish-signal` | X thread, social experiment | Compliant 3-part thread |
| `long-horizon-account` | Custodial or long-horizon account | Account review with guardrails |
| `liquidation-plan` | Hard deadline, forced exit | Staged exit schedule |

---

## Disclaimer

This is a decision-support framework, not financial advice.

See `DISCLAIMER.md` for the full disclaimer.

---

## Contributing

See `CONTRIBUTING.md`.

---

## License

MIT — see `LICENSE`.
