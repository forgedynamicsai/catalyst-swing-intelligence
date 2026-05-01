# Which Mode Should I Use?

Use this guide when you know the market question but not the correct skill mode.

---

## Fast Routing

| User intent | Use this mode |
|---|---|
| "What is the market or crowd saying about this theme?" | `crowd-scan` |
| "Is this a real catalyst or just social media noise?" | `crowd-scan` |
| "How strong is the crowd signal evidence?" | `crowd-scan` |
| "Build a trade thesis from scratch." | `thesis-build` |
| "Should I enter now or wait?" | `thesis-build` (entry quality scoring) |
| "Should I hold through earnings?" | `earnings-gate` |
| "One position is getting very large." | `concentration-check` |
| "What is the market regime right now?" | `macro-first` |
| "I have cash after a trim. What do I build next?" | `next-cycle` |
| "There is a geopolitical event. What is the market impact?" | `geopolitical-catalyst` |
| "I'm second-guessing a trim I just made." | `regret-check` |
| "Write a social media post about this thesis." | `publish-signal` |
| "This is a long-term account, not a swing account." | `long-horizon-account` |
| "I have a hard deadline for full liquidity." | `liquidation-plan` |

---

## Rule of Thumb

- Start with `macro-first` before building any new cycle.
- Use `crowd-scan` before `thesis-build` if the idea came from social media or community discussion.
- Use `thesis-build` before risking any capital.
- Use `concentration-check` when one position exceeds 30% of the account.
- Use `earnings-gate` 1–5 days before any binary earnings event.
- Use `liquidation-plan` whenever a hard deadline exists.
- Never apply `thesis-build` or `next-cycle` logic to a long-horizon account. Use `long-horizon-account` instead.

---

## Mode Dependency Map

Some modes should run in sequence:

```
macro-first
    ↓
crowd-scan  →  thesis-build  →  staged-position-entry (companion skill)
                    ↓
              earnings-gate  →  thesis-break-protocol (companion skill)
                    ↓
             concentration-check
                    ↓
               next-cycle
```

`regret-check`, `publish-signal`, `geopolitical-catalyst`, `liquidation-plan`, and
`long-horizon-account` can be invoked independently at any point.

---

## Important Distinction

`crowd-scan` scores the quality of the crowd signal — not the attractiveness of a security.

A high Crowd Signal Quality Score means the narrative is coherent and well-evidenced.

It does not mean you should buy, sell, or hold anything.

Separate analysis is always required before any capital decision.

See `docs/crowd-signal-scoring.md` for the full scoring model.
