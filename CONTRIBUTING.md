# Contributing

Contributions are welcome.

---

## Good contributions

- improve decision quality in any mode
- make trigger language clearer and more specific
- reduce ambiguity in output contracts
- add reusable generic examples (no real personal holdings)
- improve disclaimer and safety language
- generalize personal workflows into public patterns
- fix broken markdown formatting
- add new modes that fit the catalyst-driven swing trading scope
- improve the personalization template with new useful fields

## Bad contributions

- add specific stock picks as recommendations
- add hype language or promotional framing
- remove or weaken risk controls
- hardcode personal financial situations into public files
- turn the skill into financial advice
- add unsupported claims about market behavior
- commit `PERSONALIZATION.local.md` or any private config
- add personal names, family details, account values, or holdings

---

## Pull Request Standard

Every PR should explain:

1. What behavior changes?
2. Why is it useful to a general user, not just the contributor?
3. What edge case does it improve?
4. Does it introduce any personal or private information?
5. Does it preserve the public/private boundary?

---

## Public/Private Boundary Rule

The `SKILL.md` and `PERSONALIZATION.example.md` files are the only files
intended for public distribution. All personal context belongs in
`PERSONALIZATION.local.md`, which is gitignored.

If you are unsure whether a detail is private, classify it as private.

A stranger should be able to use `SKILL.md` and `PERSONALIZATION.example.md`
without editing out someone else's life.
