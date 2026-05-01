# Contributing

Contributions are welcome.

---

## Before Opening a PR

Read:

- [Maintainer Policy](docs/maintainer-policy.md)
- [Contributor Evaluation Checklist](docs/contributor-evaluation-checklist.md)
- [Legal Risk Release Checklist](docs/legal-risk-release-checklist.md)
- [Testing Guide](docs/testing-guide.md)

Run:

```bash
python -m unittest discover -s tests
```

---

## Do Not Submit

Do not submit:

- buy/sell/hold recommendations,
- purchase or investment recommendations,
- position sizing,
- price targets,
- expected returns,
- alpha or market-beating claims,
- personal holdings,
- account balances,
- cost basis,
- family details,
- private deadlines,
- credentials,
- `.env` files,
- `PERSONALIZATION.local.md`,
- brokerage or wallet integrations,
- paid API requirements for core functionality,
- or scraping workflows that bypass logins, paywalls, or access restrictions.

---

---

## Good Contributions

- improve decision quality in any mode
- make trigger language clearer and more specific
- reduce ambiguity in output contracts
- add reusable generic examples (fictional tickers, no real holdings)
- improve disclaimer and safety language
- generalize personal workflows into public patterns
- add new modes that fit the catalyst-driven swing trading scope
- improve the personalization template with new useful null-value fields
- strengthen the public/private boundary
- add or improve evaluation tests

---

## Bad Contributions

- add specific stock picks or current market calls for real securities
- add hype, performance claims, or alpha language
- remove or weaken risk controls or disclaimers
- hardcode personal financial situations into public files
- turn the skill into financial advice or a trade recommendation service
- commit `PERSONALIZATION.local.md` or any private config file
- add personal names, family details, account values, holdings, or deadlines
- use the Crowd Signal Quality Score as a buy/sell/hold score
- use signal trajectory to forecast price, return, fair value, or downside risk
- collapse crowd signal quality, security risk, and trade decision into one score

---

## Do Not Submit

Please do not submit PRs that contain:

- personal financial plans or private portfolio data
- current holdings, cost basis, or account balances
- family or household details
- private deadlines or life-event context
- stock recommendations or price targets for real securities
- performance claims ("this skill beats the market", "alpha-generating")
- hype language or promotional framing
- screenshots or exports containing private data
- buy/sell/hold calls for real securities
- paid signal language (paid Discord, paid newsletter, paid trade calls)
- brokerage affiliate or referral links
- sponsored issuer or token promotion
- claims of guaranteed performance or prediction accuracy
- references to the maintainer's government title, agency affiliation,
  official duties, diplomatic role, or public-service position

---

## Public/Private Boundary Rule

`SKILL.md` and `PERSONALIZATION.example.md` are the only files intended
for public distribution.

All personal context belongs in `PERSONALIZATION.local.md`, which is gitignored.

A stranger should be able to use `SKILL.md` without editing out someone else's life.

If you are unsure whether a detail is private, classify it as private.

---

## Pull Request Standard

Every PR should explain:

1. What behavior changes?
2. Why is it useful to a general user (not just the contributor)?
3. What edge case does it improve?
4. Does it introduce any personal or private information?
5. Does it preserve the public/private boundary?
6. Does it preserve the Crowd Signal Quality ≠ Security Risk ≠ Trade Decision distinction?
7. Has the contributor evaluation checklist been reviewed?
8. Has the legal/regulatory release checklist been reviewed for any edge cases?

---

## Crowd Signal Scoring Contributions

Contributions to the crowd-scan mode must preserve:

- Crowd Signal Quality Score as a signal-quality measure only (not a buy score)
- Signal trajectory as lifecycle classification only (not a price forecast)
- Three-layer separation: Crowd Intelligence → Market Transmission → Trade Fit
- Trade Fit as a signal-routing decision — not a buy/sell/hold recommendation
- The "not a buy/sell/hold recommendation" reminder in every crowd-scan output

---

## License

By submitting a contribution, you agree to license your work under the same
license as this project.
