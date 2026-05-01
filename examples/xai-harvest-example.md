# xAI Harvest Adapter — Fictional Example

**This is a fictional example for demonstration only.**
**All data is made up. Not financial advice. Do not trade on this.**

## Scenario

A trader wants to assess the crowd signal around "GPU shortage easing in 2025" using the xAI harvest adapter.

## Command

```bash
export XAI_API_KEY="xai_..."  # Set real API key

python tools/csi/csi.py harvest-xai "GPU shortage easing in 2025" \
  --auto-score \
  --budget-usd 1.50 \
  --output evidence/gpu-shortage-easing-2025-xai-evidence.md
```

## Output: Fictional Evidence Table

(This is what Grok might return, completely fictional)

```
| claim | source_name | source_url | source_class | source_date | source_type | independence_rating | evidence_quality | specificity | catalyst_alignment | dissent_quality | time_signal | is_duplicate | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Company X GPU shipments increased 15% YoY in Q4 2024 | Company X Example IR | https://example.com/company-x-earnings-q4 | company_ir | 2025-01-15 | news | 18 | 20 | 18 | 9 | 1 | 7 | false | From earnings report; quantified. Fictional example. |
| Spot prices for Example GPU Model fell 8% in January | Example Tech Research | https://example.com/gpu-spot-prices | trade_publication | 2025-01-20 | analysis | 14 | 17 | 19 | 8 | 2 | 8 | false | Market data analysis. Fictional example. |
| AI startups report easier GPU procurement | Example Tech Publication | https://example.com/startup-gpu-access | trade_publication | 2025-01-18 | news | 16 | 15 | 12 | 7 | 3 | 7 | false | Survey of 15 startups. Fictional example. |
| r/MachineLearning: "Finally got GPUs without 6-month wait" | Reddit | https://example.com/reddit-ml-gpu | investing_forum | 2025-01-19 | social | 8 | 12 | 8 | 6 | 4 | 5 | true | Anecdotal; also appears on social. Fictional example. |
| "GPU crunch is over" trending with 50K posts | Social Platform | https://example.com/social-gpu-trend | social_media | 2025-01-20 | social | 6 | 8 | 4 | 5 | 5 | 10 | false | Narrative velocity signal, not evidence. Fictional example. |
| Bank B upgrades semiconductor outlook | Example News Wire | https://example.com/bank-b-chips | major_news | 2025-01-17 | news | 17 | 16 | 10 | 7 | 3 | 6 | false | Broad sector view, not GPU-specific. Fictional example. |
| Chip Supplier Y equipment orders exceed forecast | Example News Wire | https://example.com/chip-supplier-y-orders | major_news | 2025-01-16 | news | 17 | 17 | 14 | 6 | 2 | 8 | false | Leading indicator for GPU supply. Fictional example. |
| Prediction market contract "GPU shortage ends Q1 2025" 72% YES | Example Prediction Market | https://example.com/prediction-market-gpu | prediction_market | 2025-01-20 | prediction | 12 | 11 | 5 | 8 | 4 | 9 | false | Crowd-sourced betting; only 24 hours old. Fictional example. |
| Research Firm A analyst: "GPU supply normalized" | Research Firm A | https://example.com/research-firm-a-analyst | pundit | 2025-01-19 | analysis | 14 | 13 | 7 | 7 | 3 | 7 | false | Expert commentary. Fictional example. |
| Company X social media sentiment shifted positive | Example Sentiment Service | https://example.com/company-x-sentiment | market_data | 2025-01-20 | data | 10 | 12 | 6 | 6 | 2 | 8 | false | AI-generated sentiment score. Fictional example. |
| (No primary SEC filings found on GPU shortage) | — | — | primary_filing | — | — | — | — | — | — | — | — | false | Lack of filings on specific topic |
| (No earnings transcript mentions supply ease) | — | — | earnings_transcript | — | — | — | — | — | — | — | — | false | Too recent for transcript availability |
| (No whale positioning data found) | — | — | whale_positioning | — | — | — | — | — | — | — | — | false | No major fund moves disclosed |
```

## Scoring Result (Fictional)

```
Crowd Signal Quality Score: 62/100

Source Coverage Grade: B
- Primary factual: 2 sources (Company X Example IR, Chip Supplier Y orders)
- News & analysis: 4 sources (Example Tech Publication, Bank B, Research Firm A, major news)
- Crowd & forum: 2 sources (Reddit, social sentiment)
- Prediction markets: 1 source (Example Prediction Market)
- Missing: Primary SEC filings, whale positioning, copy trading data

Evidence Quality: MODERATE
- Quantified claims: 4 (Company X +15%, Example GPU Model -8%, Chip Supplier Y forecast, market sentiment)
- Anecdotal claims: 3 (startups, Reddit, social platform)
- Vague claims: 3 (analyst opinion, trend, sentiment)

Duplicate Risk: LOW
- Only 1 duplicate detected (Reddit/Twitter overlap on "easier access")
- Rest are independent sources

Signal Classification: MONITOR
- Score of 62 is above 35 (passes rejection threshold)
- Coverage grade B is good but not excellent (A would require wider source diversity)
- Recommendation: Accumulate more evidence, especially from SEC filings and whale positioning

Crowd Signal Confidence: STANDARD
- 10 unique sources (good)
- Multiple source classes represented (very good)
- Clear evidence of narrative shift (good)
- But: Only 24 hours of data (too recent for high confidence)

Non-Advisory Disclaimer:
This is crowd signal assessment only. The score does NOT recommend buying, selling, or holding any security.
Crowd Signal Quality ≠ Security Risk ≠ Trade Decision. Use your own fundamental analysis.
```

## Next Steps (from --auto-score output)

```
Observation saved to: data/csi/gpu-shortage-easing-2025-20250120-v1.jsonl
Report saved to: reports/csi/gpu-shortage-easing-2025-xai-report.md

To track outcome:
  python tools/csi/csi.py outcome gpu-shortage-easing-2025-20250120-v1 \
    --event-confirmed true \
    --narrative-mainstreamed true \
    --trajectory-correct true \
    --catalyst-occurred true \
    --transmission-confirmed yes \
    --usefulness useful

To review this month's signals:
  python tools/csi/csi.py list --month 2025-01
  python tools/csi/csi.py monthly-review --month 2025-01 --output playbooks/2025-01-review.md

Cost logged to: data/csi/xai_costs.jsonl
Actual request cost: $0.0041
```

## Cost Log Entry

```json
{
  "created_at": "2025-01-20T14:32:00Z",
  "theme": "GPU shortage easing in 2025",
  "model": "grok-3",
  "tools": ["x_search", "web_search"],
  "cost_usd": 0.0041,
  "raw_response_path": "harvests/xai/20250120-143200-gpu-shortage-easing-2025-raw-response.json",
  "evidence_md_path": "evidence/gpu-shortage-easing-2025-xai-evidence.md"
}
```

## What This Is NOT

This example is NOT financial advice. It:
- ❌ Does NOT recommend buying or selling any GPU company stock
- ❌ Does NOT suggest position sizing
- ❌ Does NOT claim the GPU shortage will definitely ease
- ❌ Does NOT predict stock price moves
- ❌ Does NOT guarantee any outcome

## What This IS

This example IS a crowd signal assessment. It:
- ✅ Documents what the crowd is saying
- ✅ Rates the quality and diversity of evidence
- ✅ Identifies signal strength and narrative shift
- ✅ Flags where evidence is weak (filings, whale positioning)
- ✅ Allows you to feed this into YOUR own analysis

## Key Insights (Analytical, Not Advisory)

Observations:
1. **Narrative shift is real:** Multiple independent sources confirm "shortage easing"
2. **Evidence is mixed:** Strong on market-level indicators (Chip Supplier Y orders, analyst commentary), weaker on company-specific filings
3. **Virality ≠ validity:** X trending (#GPUShortageOver) shows narrative attention, but needs fact-checking
4. **Time lag matters:** Polymarket contract is only 24 hours old; too early to trust
5. **Gap in whale positioning:** No institutional moves disclosed yet—early indicator missing

The trader should:
- ✅ Treat this as ONE input to their analysis
- ✅ Cross-check with their own fundamental research
- ✅ Monitor for whale positioning (when/if disclosed)
- ✅ Revisit in 2-4 weeks with more outcome data
- ✅ Track whether this signal was useful (via `outcome` command)

---

**Remember:** Crowd signals are evidence, not predictions. Use them to inform your research, not to make decisions.
