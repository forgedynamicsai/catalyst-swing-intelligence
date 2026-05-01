# Contributor Evaluation Checklist

Use this checklist before opening or merging a pull request.

---

## 1. Public/Private Boundary

- [ ] Does this PR avoid personal names?
- [ ] Does this PR avoid real account holdings?
- [ ] Does this PR avoid cost basis, balances, private deadlines, and family details?
- [ ] Does this PR avoid copying `PERSONALIZATION.local.md` or any private config?
- [ ] If personalization is needed, does it belong in `PERSONALIZATION.example.md` as a null-value placeholder with an illustrative comment?

---

## 2. Skill Quality

- [ ] Does this change improve decision quality for a general user?
- [ ] Does it reduce ambiguity in mode routing or output contracts?
- [ ] Does it preserve all existing risk controls?
- [ ] Does it preserve thesis-broken conditions?
- [ ] Does it avoid turning the skill into financial advice?
- [ ] Does it preserve the three-layer distinction: Crowd Signal Quality ≠ Security Risk ≠ Trade Decision?
- [ ] Does it avoid using the Crowd Signal Quality Score as a buy/sell/hold score?
- [ ] Does it avoid interpolation for price forecasts, fair value, or expected return?
- [ ] Does it preserve signal trajectory as lifecycle classification only, not price prediction?

---

## 3. Example Quality

- [ ] Are examples fictional?
- [ ] Do examples avoid current stock picks for real securities?
- [ ] Do examples use placeholders (TICKER_A, ETF_B, Company X, Sector Y, Catalyst Z)?
- [ ] Do examples show both input and expected output shape?
- [ ] Do examples include the disclaimer: "This is a fictional example and not financial advice"?
- [ ] Do `crowd-scan` examples include Crowd Signal Quality Score, penalties, trajectory, and trade-fit classification as separate layers?

---

## 4. Risk and Disclaimer

- [ ] Does the PR preserve "not financial advice" framing throughout?
- [ ] Does it avoid performance claims, alpha language, and market-beating assertions?
- [ ] Does it avoid hype or promotional framing?
- [ ] Does it avoid implying the skill predicts returns, reduces losses, or guarantees outcomes?
- [ ] Does it avoid paid-signal, paid-Discord, paid-newsletter, brokerage-affiliate, issuer-promotion, or sponsorship language?
- [ ] Does it avoid using the maintainer's government title, agency affiliation, or official position to promote the project?

---

## 5. Legal / Regulatory Boundary

- [ ] Does this PR avoid any language that would make the project look like personalized investment advice?
- [ ] Does it avoid any language suggesting a securities recommendation service?
- [ ] Does it avoid implying the skill is suitable for a specific user's risk tolerance, age, income, or financial situation?
- [ ] Has the `docs/legal-risk-release-checklist.md` been reviewed for any edge cases this PR introduces?

---

## 6. Merge Decision

Approve a PR only if the change is:

- reusable by a general user (not personalized to a specific person)
- safer or equally safe as the prior version
- clearer in routing or output structure
- does not leak private context
- preserves all risk controls and the public/private boundary

Reject a PR that:

- adds personal financial situations
- adds stock picks or current market calls
- adds performance claims or alpha language
- removes disclaimers or risk controls
- adds paid-advice, affiliate, or issuer-promotion language
- adds government title or agency endorsement
