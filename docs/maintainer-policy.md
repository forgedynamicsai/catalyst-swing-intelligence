# Maintainer Policy

This project accepts contributions that improve crowd-signal assessment.

This project rejects contributions that turn the tool into:

- a stock picker,
- a trading bot,
- a signal service,
- a financial advice system,
- a portfolio allocator,
- a price-target generator,
- a paid recommendation product,
- or a private-data collection system.

---

## Core Boundaries

The official repository must preserve:

```text
Crowd Signal Quality ≠ Security Risk ≠ Trade Decision
```

```text
Crowd Signal Playbook ≠ Investment Playbook
```

```text
Search-first, API-optional.
```

```text
No evidence, no full-confidence score.
```

---

## Merge Requirements

A PR may merge only if:

1. Tests pass (`python -m unittest discover -s tests`).
2. Non-advisory boundaries are preserved.
3. Private-data boundaries are preserved.
4. The change improves clarity, safety, operability, evidence quality, scoring consistency, or documentation.
5. The change does not create required paid API dependencies.
6. The change does not add hidden external-service dependencies.
7. The change does not require credentials, brokerage access, wallet access, email access, or private account access.
8. The change does not claim predictive performance, alpha, expected return, or market-beating ability.

---

## Maintainer Rights

Maintainers may close issues or PRs that:

- request buy/sell/hold recommendations,
- add real ticker recommendations,
- add performance claims,
- add personal financial data,
- introduce credentialed or private data access,
- weaken the non-advisory boundary,
- weaken the privacy boundary,
- remove required disclaimers,
- or convert the project into a recommendation service.

---

## Classification Language

Use:

```text
analysis-ready / monitor / reject
```

Do not use advisory-sounding classification language such as:

```text
tradeable / watchlist
```

except in changelog/history or tests that verify old terms are absent.

---

## Contributor Expectations

Contributors should:

- use fictional or historical examples,
- include tests for behavioral changes,
- update documentation when workflows change,
- preserve low-cost local-first operation,
- and explain how their change improves crowd-signal assessment.

---

## Release Discipline

Each release should include:

- summary of user-facing changes,
- test status,
- known limitations,
- non-advisory reminder,
- and any migration notes.

---

This project evaluates crowd-signal usefulness. It does not recommend purchases, investments, trades, position sizing, or buy/sell/hold actions.
