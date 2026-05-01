# Example: crowd-scan

> This is a fictional example for demonstrating the skill format. It is not financial advice.
> Tickers, themes, and scenarios are illustrative only.

---

## Input

```
Use swing-intelligence crowd-scan mode.

Theme: Multiple independent accounts on X and Reddit are posting about a specific
industrial commodity facing a supply shock due to export restrictions from a major
producing country. The posts are citing official government announcements, analyst
notes, and commodity price data — not just each other.
```

---

## Expected Output Shape

```markdown
## Crowd Signal
- Source: X/finTwit (accounts: [listed]), Reddit r/investing, r/stocks
- Theme: Supply shock in COMMODITY_X due to export restrictions
- Mechanism: Export controls reduce global supply → inventory drawdown →
  spot price increase → margin expansion for domestic producers
- Timing window: 1–3 months (inventory depletion timeline)
- Evidence quality: official government announcement + analyst notes + commodity price data
- Convergence score: 7/9 (volume: 2, independence: 3, specificity: 2)
- Priced-in risk: partially priced — spot price moved 8%, equities lagged

## Best Expressions
1. TICKER_A — domestic producer, direct margin beneficiary
2. ETF_B — sector ETF with concentrated exposure to TICKER_A and peers
3. TICKER_C — downstream processor that could benefit from supply tightness

## Rejected / Too Loose
- TICKER_D — vague thematic exposure, no direct earnings link
- ETF_E — too diversified; COMMODITY_X is < 5% of holdings

## Final Tradeable Version
TICKER_A on pullback with confirmed entry zone. ETF_B as lower-conviction
diversifier. Thesis-broken condition: export restrictions lifted or domestic
supply increases materially before inventory drawdown occurs.
```
