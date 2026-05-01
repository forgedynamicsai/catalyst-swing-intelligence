# Example: concentration-check

> This is a fictional example and not financial advice.
> All tickers, positions, and account values are illustrative only.

---

## Input

```
Use concentration-check.

TICKER_A is now 47% of my swing account after a strong run.
Earnings are in 6 days. I entered at $80, current price is $118.
```

---

## Expected Output Shape

```markdown
## Concentration Review

- Position: TICKER_A
- Current weight: 47% of swing account
- Unrealized gain: +47.5%
- Event risk: Binary earnings in 6 days
- +10% impact on account: +$4,700 per $100,000 account (position-level)
- −10% impact on account: −$4,700 per $100,000 account
- −15% gap risk (earnings miss): −$7,050 per $100,000 account

## Concentration Status

47% exceeds the 40% threshold that requires explicit written justification.
This position also triggers the earnings-gate rule.

Run `earnings-gate` mode for the full pre-earnings decision tree.

## Recommendation

- Trim: Yes — reduce from 47% to approximately 28–30%
  Suggested trim: approximately 35–40% of current shares held
- Hold remaining core: Yes — thesis intact, catalyst ahead
- Add before earnings: No — position is oversized and no-profit-cushion
  rule does not apply here (profit cushion exists), but concentration
  does exceed threshold
- Reason: A position at 47% with a binary earnings event exposes the account
  to gap risk that exceeds acceptable single-position exposure. Trimming
  converts account-level risk into a controlled core position. If earnings
  are strong, the remaining core captures the upside. If earnings disappoint,
  the account is not destroyed by one print.
- Post-event action: If thesis confirmed post-earnings, reassess add-more zone
  at next pullback with fresh entry analysis.
```
