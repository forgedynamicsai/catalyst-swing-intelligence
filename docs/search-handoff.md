# Search Handoff Pattern

Design pattern for instructing LLMs to harvest evidence from search APIs.

**Note:** This pattern is documented for users who choose to use LLM search APIs
(such as xAI/Grok). The core CSI workflow is search-first and works without any
paid API — see `tools/csi/csi.py wizard` and `tools/csi/csi.py queries`.

## Problem

Manual search for crowd signal evidence is slow. Using an LLM to orchestrate search APIs is fast, but requires careful prompt design to avoid:
- Hallucinated sources
- Confusing virality with evidence quality
- Investment recommendations disguised as analysis
- Echo chambers where multiple sources cite one origin

## Solution: Search Handoff Prompt

A "search handoff" prompt instructs an LLM to:
1. Use multiple, independent search tools
2. Distinguish signal strength from evidence quality
3. Mark unavailable source classes explicitly
4. Avoid advisory language
5. Output only structured data (markdown table)

## Pattern Elements

### 1. Search Tool Diversity

Instruct the LLM to use multiple tools:

```
- Use X/social search to find narrative velocity and source emergence
- Use web/news search to find source diversity and confirmation
```

Why both?
- **X/social:** Fast signal emergence, early narrative shifts
- **Web/news:** Source credibility, official statements, filings

Grok's Responses API includes both `x_search` and `web_search` tools.

### 2. Signal ≠ Evidence Quality

Explicitly distinguish virality from credibility:

```
X virality (retweets, likes) is a SIGNAL OF NARRATIVE VELOCITY, NOT EVIDENCE QUALITY.
Engagement metrics do NOT validate claims — cross-check with news/filings.
```

Why? Social media engagement reflects attention, not truth. A fabricated claim can go viral.

### 3. Source Emergence Detection

Instruct the LLM to identify echo chambers:

```
Identify whether multiple posts trace back to one original source (avoid double-counting).
Mark duplicates as "true" if multiple sources report the same fact from one origin.
```

Why? If 100 posts cite one analyst, that's 1 source, not 100.

### 4. Explicit Unavailability

Instruct the LLM to mark missing source classes:

```
If you cannot find evidence for a class, mark it as unavailable — do NOT invent sources.
Every source must be real. No fabricated URLs or organizations.
```

Why? Missing data is more useful than hallucinated data. It signals where evidence is weak.

### 5. Structure-Only Output

Instruct the LLM to return ONLY structured output:

```
Return ONLY a CSI-compatible markdown evidence table.
No introduction, no explanation, no summary.
```

Why? Parsing is deterministic. No need to extract meaning from prose.

### 6. Non-Advisory Boundary

Explicitly prohibit advisory language:

```
Output evidence about market signals, NOT investment recommendations.
Do NOT provide buy/sell/hold advice.
Do NOT recommend purchases, investments, trades, position sizing, or specific companies to buy.
Do NOT provide price targets, expected returns, or alpha claims.
```

Why? Evidence and recommendations are different. This tool documents signals; the user decides.

## CSI Evidence Schema

Structure the output as a CSI-compatible markdown table:

```
| claim | source_name | source_url | source_class | source_date | source_type | \
independence_rating | evidence_quality | specificity | catalyst_alignment | dissent_quality | \
time_signal | is_duplicate | notes |
```

Column definitions:

| Column | Type | Range | Purpose |
|--------|------|-------|---------|
| `claim` | string | — | The specific claim or signal |
| `source_name` | string | — | Organization/person (e.g., "Reuters", "NVIDIA IR") |
| `source_url` | string | — | Full URL if available, empty if not found |
| `source_class` | enum | 13 classes | Category of source (filing, news, forum, etc.) |
| `source_date` | ISO 8601 | YYYY-MM-DD | When the source was published |
| `source_type` | string | news, forum, filing, social, etc. | Type of content |
| `independence_rating` | int | 0-20 | How independent from bias (0=biased, 20=independent) |
| `evidence_quality` | int | 0-20 | Credibility (0=rumor, 10=credible, 20=primary) |
| `specificity` | int | 0-20 | Quantified vs. vague (0=vague, 20=quantified) |
| `catalyst_alignment` | int | 0-10 | How well evidence maps to your theme |
| `dissent_quality` | int | 0-5 | Quality of opposing view, if present |
| `time_signal` | int | 0-10 | Urgency/recency (0=stale, 10=breaking) |
| `is_duplicate` | bool | true/false | Same fact from downstream source? |
| `notes` | string | — | Context, caveats, calculation basis |

## Source Class Coverage

Instruct the LLM to attempt coverage across all source classes:

```
Attempt to find evidence across these source classes:
  * primary_filing (SEC filings, 10-K, 10-Q, 8-K)
  * earnings_transcript (earnings call transcripts)
  * company_ir (company investor relations)
  * major_news (Reuters, Bloomberg, WSJ, FT)
  * trade_publication (industry-specific news)
  * investing_forum (Reddit, Seeking Alpha, StockTwits)
  * social_media (X/Twitter, LinkedIn, other social)
  * prediction_market (Polymarket, Kalshi, Metaculus)
  * pundit (analyst calls, expert commentary)
  * whale_positioning (institutional moves, 13F filings, options)
  * copy_trading (retail flow, eToro popular investor)
  * market_data (short interest, volume, price action)
  * unknown (anything that doesn't fit above)
```

Why? Balanced source coverage is a proxy for signal quality. All-social or all-news are both weak.

## Implementation: xAI Grok

The CSI harvest adapter implements this pattern for xAI/Grok:

```python
# tools/csi/xai_harvest.py::build_harvest_prompt()
def build_harvest_prompt(theme: str, max_sources: int = 20) -> str:
    """
    Build a prompt that instructs Grok to harvest evidence for a theme.
    
    Key instructions:
    - Use X/social search for narrative velocity
    - Use web/news search for source diversity
    - Distinguish X virality from evidence quality
    - Mark source classes as unavailable if not found
    - Output ONLY a CSI-compatible markdown evidence table
    - NOT provide buy/sell/hold advice
    """
```

Call with:
```bash
python tools/csi/csi.py harvest-xai "your theme" --auto-score
```

## Validation and Feedback

After harvest, CSI validates the output:

1. **Schema validation** (`tools/csi/validation.py`)
   - All required columns present
   - Numeric fields in valid ranges
   - Source classes are recognized

2. **Advisory check** (policy gate)
   - Detects phrases like "buy now", "sell now", "price target"
   - Warns but doesn't reject (context matters)

3. **Scoring**
   - Source coverage graded A–F
   - Evidence quality rated 0-100
   - Crowd signal classification: analysis-ready / monitor / reject

## Anti-Patterns

❌ **Don't:** Trust X engagement as evidence
```
"This post got 1M retweets, so it must be true"
```
✅ **Do:** Treat engagement as signal emergence
```
"This narrative is spreading rapidly. Cross-check with news/filings."
```

❌ **Don't:** Return prose analysis
```
"Based on my analysis, X users seem bullish on AI data centers..."
```
✅ **Do:** Return structured evidence
```
| "Data centers need more power" | AnandTech | http://... | trade_publication | 2025-01-15 | ... |
```

❌ **Don't:** Invent sources
```
"I couldn't find data on whale positioning, so I guessed some fund names"
```
✅ **Do:** Mark unavailable
```
(Omit rows where whale_positioning source couldn't be found, or note "unknown")
```

❌ **Don't:** Make buy/sell recommendations
```
"This signal is strong enough to buy the stock"
```
✅ **Do:** Present evidence
```
"Multiple sources confirm the theme. Evidence quality grade: B. Classification: analysis-ready."
```

## References

- [xAI Responses API](https://docs.x.ai/) — Official API docs
- [CSI Evidence Schema](../tools/csi/README.md) — Full column reference
- [xAI Harvest Adapter](./xai-harvest-adapter.md) — Implementation in CSI
- [Memory Flywheel](../tools/csi/memory.py) — Post-harvest tracking and learning
