# Pull Request Checklist

## What changed?

-

## Why is this useful?

-

## Type of change

- [ ] Documentation
- [ ] Skill instruction update
- [ ] CLI/scoring code
- [ ] Validation/import/wizard UX
- [ ] Memory/playbook logic
- [ ] Tests
- [ ] Examples
- [ ] Governance / repo maintenance
- [ ] Other

---

## Non-Advisory Boundary

- [ ] This PR does not include buy/sell/hold recommendations.
- [ ] This PR does not suggest purchases, investments, trades, position sizing, companies to buy, price targets, expected returns, alpha, or market-beating claims.
- [ ] This PR preserves: `Crowd Signal Quality ≠ Security Risk ≠ Trade Decision`.
- [ ] This PR preserves: `Crowd Signal Playbook ≠ Investment Playbook`.
- [ ] This PR uses `analysis-ready / monitor / reject` rather than advisory-sounding language.

## Privacy Boundary

- [ ] This PR does not include personal holdings.
- [ ] This PR does not include account values, cost basis, family details, private deadlines, or private personalization files.
- [ ] This PR does not include `PERSONALIZATION.local.md`, `.env`, credentials, brokerage, wallet, email, or private account data.

## Source / Evidence Boundary

- [ ] Examples are fictional, historical, or clearly illustrative.
- [ ] Any source-acquisition language is search-first and API-optional.
- [ ] The PR does not claim complete market coverage.
- [ ] The PR does not add scraping behind logins, paywalls, or credentialed sources.
- [ ] The PR does not add required paid APIs or required external services.

## Tests

- [ ] I ran `python -m unittest discover -s tests`.
- [ ] Tests pass.
- [ ] I updated or added tests for changed behavior.

## Notes for Maintainer

-
