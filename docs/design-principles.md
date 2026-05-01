# Design Principles

---

## 1. Separate methodology from biography

The skill should work for any disciplined swing trader, not just the person who
wrote it. Personal context belongs in `PERSONALIZATION.local.md`. Reusable
decision logic belongs in `SKILL.md`.

## 2. Prefer reusable decision frameworks over hardcoded examples

Examples that name specific tickers, accounts, or events will rot. Frameworks
that name the mechanism survive. Build the framework; let the user supply the
example.

## 3. Require explicit risk controls

Every mode that deploys capital or sizes a position must include a risk gate:
concentration check, stop loss, thesis-broken condition, or hard deadline.
Risk controls are not optional and cannot be removed by personalization.

## 4. Treat crowd intelligence as signal, not advice

Crowd signals are inputs to analysis. They are never outputs. The skill scores
convergence, flags priced-in risk, and requires a mechanism — it does not
endorse the crowd's conclusion.

## 5. Preserve thesis-broken conditions

Every thesis must have a specific invalidation condition before the trade is
entered. Generic risks ("market volatility") are rejected. This protects the
user from rationalization and exit hesitation.

## 6. Do not let public skill logic depend on private user context

The skill must be usable without `PERSONALIZATION.local.md`. Modes that reference
personal defaults must have a graceful fallback that prompts the user for the
missing context inline.

## 7. Keep modes narrow and activation triggers clear

A mode that does too much will false-trigger or miss its trigger. Each mode
should answer one type of question. Activation triggers should be specific
enough that a model can route to the right mode without ambiguity.

## 8. Financial disclaimer is mandatory on all published output

Any mode that produces output intended for external publication (e.g.,
`publish-signal`) must include all five required disclaimers. This is not
configurable and cannot be removed by personalization.
