# Example: thesis-build

> This is a fictional example for demonstrating the skill format. It is not financial advice.
> Tickers, themes, and scenarios are illustrative only.

---

## Input

```
Use swing-intelligence thesis-build mode.

I want to build a swing trade on TICKER_A, a mid-cap industrial company.
The thesis is that an upcoming earnings report will confirm accelerating
backlog growth driven by infrastructure spending. The stock has pulled back
15% from its recent high on no fundamental news.
```

---

## Expected Output Shape

```markdown
## Thesis
- Ticker: TICKER_A
- Primary catalyst: Q[X] earnings — backlog growth confirmation
- Catalyst date: [earnings date]
- Mechanism: Accelerating backlog → forward revenue visibility → multiple
  re-rating from depressed infrastructure spending discount
- Entry zone: $[X] – $[X+5] (current pullback range, no fundamental cause)
- Add-more zone: $[X-10%] if thesis intact
- Hard stop: $[X-18%] — below which pullback implies something structural
- Target / exit logic: $[prior high] on backlog confirmation; reassess at +25%
- Catalyst calendar: Earnings [date], sector conference [date], next CPI [date]
- Position size: 12% of swing account (moderate conviction, binary catalyst)
- Risk/reward: 2.8:1 at entry zone midpoint
- Thesis-broken conditions:
    - Backlog growth decelerates vs. prior quarter
    - Management lowers full-year guidance
    - Infrastructure spending category shows demand softness in commentary
- Exit deadline: [date 8 weeks out] — do not carry through next earnings

## Entry quality score: 8/10
## Entry action: Enter with planned tranche; define add-more zones before first share
```
