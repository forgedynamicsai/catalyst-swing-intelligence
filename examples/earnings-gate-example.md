# Example: earnings-gate

> This is a fictional example for demonstrating the skill format. It is not financial advice.
> Tickers, themes, and scenarios are illustrative only.

---

## Input

```
Use swing-intelligence earnings-gate mode.

TICKER_A is 5 days from earnings. I entered at $90. Current price is $112.
It is now 44% of my swing account. My thesis is intact — the company has been
winning contracts and growing its order book. But the position is oversized and
the catalyst is binary.
```

---

## Expected Output Shape

```markdown
## Earnings Gate
- Ticker: TICKER_A
- Earnings date: [5 days out]
- Position size / weight: 44% of swing account
- Profit cushion: +24% unrealized gain
- Thesis status: intact
- Bull case: Contract wins accelerate, management raises guidance, margin improvement
- Bear case: Execution miss on large contract, guidance lowered due to input costs
- Key metrics to watch: Organic revenue growth, order book value, gross margin %
- Guidance threshold that would confirm thesis: Full-year guidance maintained or raised
- Guidance threshold that would break thesis: Revenue guidance cut >5%, or backlog flat
- Risk/reward at current size: Asymmetric downside at 44% weight — gap risk exceeds upside

## Action
- Hold: Yes — core position
- Trim: Yes — reduce from 44% to 28% (trim ~30% of shares)
  Rationale: Profit cushion exists; concentration exceeds 40% threshold;
  trimming converts account-level risk into a controlled core position.
- Exit: No — thesis intact
- Add: No — no profit cushion rule would not allow add before binary event

## Post-Earnings Action Plan
- If beats + guides up: Hold core, reassess add-more zone at next pullback
- If beats + guides flat: Hold core, monitor for margin commentary
- If misses or guides down: Evaluate thesis-break protocol — exit if backlog guidance cut
- Thesis-broken trigger: See thesis-broken conditions in original thesis
```
