# Example: liquidation-plan

> This is a fictional example for demonstrating the skill format. It is not financial advice.
> Tickers, themes, and scenarios are illustrative only.

---

## Input

```
Use swing-intelligence liquidation-plan mode.

I have a hard liquidity deadline of [DATE+5 months]. I currently hold:
- TICKER_A: 30% of account, entered at $80, currently $105, earnings in 6 weeks
- TICKER_B: 20% of account, entered at $45, currently $48, no upcoming catalyst
- ETF_C: 15% of account, entered at $200, currently $195, tracks a sector with
  a policy decision in 3 months
- Cash: 35% of account

I need the full account liquid by the deadline. I cannot open new positions
after [DATE+3 months].
```

---

## Expected Output Shape

```markdown
## Liquidation Plan

### Current Holdings
| Position | Weight | Entry | Current | Gain/Loss | Notes |
|---|---|---|---|---|---|
| TICKER_A | 30% | $80 | $105 | +31% | Earnings in 6 weeks |
| TICKER_B | 20% | $45 | $48 | +7% | No catalyst |
| ETF_C | 15% | $200 | $195 | -2.5% | Policy event in 3 months |
| Cash | 35% | — | — | — | Deploy nothing new |

### Hard Rules
- No new positions after [DATE+3 months]
- Full liquidation by [DATE+5 months]
- Maximum drawdown tolerated before forced exit: [user-defined]

### Trim Schedule
- TICKER_A: Hold through earnings ([DATE+6 weeks]). If thesis intact post-earnings,
  trim 50% within 2 weeks. Exit remainder by [DATE+3.5 months].
- TICKER_B: No catalyst to wait for. Trim 50% within 30 days. Exit remainder by
  [DATE+2.5 months].
- ETF_C: Hold through policy event ([DATE+3 months]). Exit within 2 weeks of event
  regardless of outcome.

### No-New-Risk Date: [DATE+3 months]
After this date: no new positions, no adds to existing positions, reduce exposure only.

### Full Exit Deadline: [DATE+5 months]
All positions closed. Account fully liquid.

### Tax Note
TICKER_A gain is short-term if held < 1 year. Evaluate whether timing exit across
a tax year boundary is material. Consult a tax professional.

### Contingency
If any position is down >15% from current price before planned exit:
apply thesis-break-protocol. Do not hold losers waiting for recovery near deadline.
```
