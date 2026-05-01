# Example: long-horizon-account

> This is a fictional example for demonstrating the skill format. It is not financial advice.
> Tickers, themes, and scenarios are illustrative only.

---

## Input

```
Use swing-intelligence long-horizon-account mode.

I have a custodial UTMA account for my child with a 10-year time horizon.
Current holdings:
- ETF_A (broad market index): 35%
- ETF_B (dividend index): 20%
- MEGA_CAP_1: 18%
- MEGA_CAP_2: 12%
- TURNAROUND_CO: 8%
- SPECULATIVE_CO: 7%

I'm wondering whether to add more to TURNAROUND_CO because the price has dropped.
```

---

## Expected Output Shape

```markdown
## Long-Horizon Account Review
- Account name: Child UTMA
- Beneficiary: [child — long-horizon beneficiary]
- Time horizon: 10 years
- Current risk level: Moderate — speculative allocation (15%) is within acceptable range

## Current Allocation Assessment
| Category | Target | Actual | Status |
|---|---|---|---|
| Core broad-market ETFs | 50–65% | 55% | On target |
| Mega-cap compounders | 25–40% | 30% | On target |
| Turnaround + moonshot | 5–15% | 15% | At upper bound |

## On TURNAROUND_CO — Should I add?

Applying turnaround add-signal checklist:
- [ ] Two consecutive quarters of positive revenue growth — UNKNOWN, requires verification
- [ ] Gross margin stops falling — UNKNOWN, requires verification
- [ ] Competitive pressure visibly easing — UNKNOWN, requires verification
- [ ] Key geography or product line stabilizing — UNKNOWN, requires verification

**Recommendation: Do not add on price alone.**

Price dropped ≠ thesis improved. Before adding, verify all four signals above.
If none are confirmed, hold current position and wait.

Adding to TURNAROUND_CO solely because the price is lower is averaging down —
a discipline violation in this account type.

## Action today
- Hold current allocation
- Do not add to TURNAROUND_CO until add-signals are confirmed
- Continue building core ETF positions with new contributions
- Do not apply swing-trading logic to any position in this account

## What not to do
- Do not treat this account as a swing account
- Do not add to speculative positions without evidence improvement
- Do not reduce ETF core because a speculative bet looks attractive
```
