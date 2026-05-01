# xAI/Grok Evidence Harvest Adapter

**This adapter is optional. The core Catalyst Swing Intelligence repo is public,
local-first, and requires no paid APIs, no xAI account, and no external services.**

Core CSI does not require xAI, Grok, paid APIs, or external services. This adapter
is an optional automation path for users who choose to provide their own `XAI_API_KEY`.
API keys are read only from environment variables, are never stored, and are never
committed to any file.

## Who This Is For

This adapter is for users who:

- already have xAI API access and want to automate evidence harvesting,
- prefer to skip manual searching and have Grok run X Search + Web Search on their behalf,
- understand that automation does not improve signal quality — only evidence completeness.

**If you do not have an `XAI_API_KEY`, ignore this file entirely.** The full CSI
workflow — queries, template, validate, score, report, observe — works without it.
Run `python tools/csi/csi.py wizard` instead.

## What It Does NOT Do

- It does not make buy/sell/hold recommendations.
- It does not replace your own judgment or fundamental analysis.
- It does not guarantee complete source coverage.
- It does not provide price targets, expected returns, or alpha claims.
- It does not store your API key.
- It does not work without your explicit `export XAI_API_KEY="..."`.

## Overview

The harvest adapter allows you to:
- Query xAI/Grok for evidence related to a market theme
- Get back a CSI-compatible markdown evidence table
- Optionally run the full scoring pipeline in one command
- Track costs to `data/csi/xai_costs.jsonl`
- Save raw API responses for audit and debugging

## Requirements

- `XAI_API_KEY` environment variable set (from xAI) — **never** a `.env` file
- No additional Python packages required (uses standard library only)

## Installation

Set your API key:
```bash
export XAI_API_KEY="your_xai_api_key_here"
```

## Usage

### Basic Harvest

```bash
python tools/csi/csi.py harvest-xai "AI data center power scarcity"
```

This will:
1. Call xAI/Grok with a harvest prompt
2. Save markdown evidence table to `evidence/csi/{slug}-xai-evidence.md`
3. Save raw response JSON to `harvests/xai/{timestamp}-{slug}-raw-response.json`
4. Log cost to `data/csi/xai_costs.jsonl`
5. Print next commands

### With Custom Output Path

```bash
python tools/csi/csi.py harvest-xai "GPU memory bandwidth constraints" \
  --output evidence/my-theme-evidence.md
```

### Auto-Score Pipeline

```bash
python tools/csi/csi.py harvest-xai "AI data center power scarcity" --auto-score
```

This runs: harvest → markdown import → validate → score → report → observe

### With Budget Warning

```bash
python tools/csi/csi.py harvest-xai "AI data center power scarcity" \
  --budget-usd 2.00 \
  --auto-score
```

The `--budget-usd` flag shows a warning but does NOT enforce a hard limit. xAI's actual cost depends on response length and model.

### Advanced Options

```bash
python tools/csi/csi.py harvest-xai "AI data center power scarcity" \
  --runtime-tools x,web \      # Default: both X Search and Web Search
  --model grok-3 \              # Default: grok-3
  --max-sources 30 \            # Hint to Grok, not enforced (default: 20)
  --output evidence.md \
  --data-dir data/csi \
  --reports-dir reports/csi \
  --auto-score
```

### Convenience Alias: `oneclick`

```bash
python tools/csi/csi.py oneclick "AI data center power scarcity"
```

Equivalent to `harvest-xai ... --auto-score` with default settings.

## Output Files

- **`evidence/csi/{slug}-xai-evidence.md`** — Markdown evidence table (CSI schema)
- **`evidence/csi/{slug}-xai-evidence.csv`** — CSV version (created by import-md if auto-score)
- **`harvests/xai/{timestamp}-{slug}-raw-response.json`** — Full xAI response for audit
- **`reports/csi/{slug}-xai-report.md`** — Crowd signal report (if auto-score)
- **`data/csi/xai_costs.jsonl`** — Cost log (appended each run)
- **`data/csi/observations.jsonl`** — Signal observation (if auto-score + observe)

## Cost Logging

Each request appends to `data/csi/xai_costs.jsonl`:

```json
{
  "created_at": "2025-01-15T14:32:00Z",
  "theme": "AI data center power scarcity",
  "model": "grok-3",
  "tools": ["x_search", "web_search"],
  "cost_usd": 0.0037756,
  "raw_response_path": "harvests/xai/20250115-143200-ai-data-center-power-scarcity-raw-response.json",
  "evidence_md_path": "evidence/csi/ai-data-center-power-scarcity-xai-evidence.md"
}
```

If xAI's response omits cost data, `cost_usd` is `null`.

## Harvest Prompt

The adapter sends Grok a detailed prompt that:
- Instructs use of X Search (for narrative velocity) and Web Search (for diversity)
- Distinguishes X virality from evidence quality
- Targets coverage across 13 source classes (filings, news, forums, etc.)
- Prohibits buy/sell/hold advice and company recommendations
- Requests markdown evidence table only
- Marks unavailable source classes explicitly

See `tools/csi/xai_harvest.py::build_harvest_prompt()` for full text.

## Search Tools

### `x` (X/Social Search)

Finds posts on X/Twitter and other social platforms. Good for:
- Narrative velocity and emerging signals
- Crowd sentiment and discussion
- First-hand market chatter

**Limitation:** X virality (retweets, likes) is NOT evidence quality. Check facts against news/filings.

### `web` (Web/News Search)

Finds published news, articles, filings, and analysis. Good for:
- Source diversity and confirmation
- Credible news from Reuters, Bloomberg, WSJ, FT
- Company IR and SEC filings
- Industry analysis

### Both (default)

Uses both tools for maximum coverage. xAI will synthesize results from both into a single markdown table.

## Non-Advisory Boundary

**IMPORTANT:** This tool outputs crowd signal evidence, NOT investment advice.

What it does:
- Documents public evidence and signals
- Tracks source quality and coverage
- Identifies narrative velocity and source emergence

What it does NOT do:
- Recommend buying or selling securities
- Suggest position sizing
- Provide price targets or expected returns
- Claim alpha or outperformance
- Recommend specific companies

The output is for crowd-signal assessment only. All scoring and reports include explicit disclaimers.

## Error Handling

### Missing API Key

```
XAI_API_KEY is not set.

Set it for this shell session:

  export XAI_API_KEY="your_api_key"

No request was sent.
```

### Authentication Failure (HTTP 401/403)

```
Error: Authentication failed. Check XAI_API_KEY.
```

### Rate Limiting (HTTP 429)

```
Error: Rate limited. Wait and retry.
```

### Invalid Model (HTTP 404)

```
Error: Model or endpoint not available.
```

### Invalid Response

```
Error: xAI response did not contain a markdown evidence table.
```

## Source Class Reference

The harvest prompt instructs Grok to categorize evidence as:

| Class | Examples |
|-------|----------|
| `primary_filing` | SEC 10-K, 10-Q, 8-K |
| `earnings_transcript` | Earnings call transcripts |
| `company_ir` | Investor relations press releases |
| `major_news` | Reuters, Bloomberg, WSJ, FT |
| `trade_publication` | Industry-specific news (AnandTech, etc.) |
| `investing_forum` | Reddit r/investing, Seeking Alpha, StockTwits |
| `social_media` | X/Twitter, LinkedIn, other social |
| `prediction_market` | Polymarket, Kalshi, Metaculus |
| `pundit` | Analyst calls, expert commentary |
| `whale_positioning` | 13F filings, institutional moves, options |
| `copy_trading` | Retail flow, eToro popular investor |
| `market_data` | Short interest, volume, price action |
| `unknown` | Does not fit above |

## Testing

All 22 tests are mocked (no real API calls):

```bash
python -m pytest tests/test_csi_xai_harvest.py -v
```

To manually test with real API (requires `XAI_API_KEY`):

```bash
# Simple harvest
python tools/csi/csi.py harvest-xai "test theme" --output /tmp/test.md

# With auto-score
python tools/csi/csi.py harvest-xai "test theme" --auto-score

# Check costs
cat data/csi/xai_costs.jsonl | jq .
```

## Architecture

**Module:** `tools/csi/xai_harvest.py` (~400 lines)

Key functions:
- `build_harvest_prompt(theme, max_sources)` — Constructs harvest instruction
- `check_api_key()` — Verifies XAI_API_KEY environment variable
- `make_request(api_key, theme, model, tools, max_sources)` — Calls xAI Responses API
- `extract_markdown_table(response)` — Parses response for markdown table
- `extract_cost_usd(response)` — Converts cost_in_usd_ticks to USD
- `save_raw_response(response, theme)` — Saves JSON for audit
- `log_cost(...)` — Appends cost entry to jsonl
- `harvest(theme, ...)` — Main command (orchestrates all above)

**Integration:** `tools/csi/csi.py`

- Adds `harvest-xai` subcommand with 8 arguments
- Adds `oneclick` convenience alias
- Lazy imports `xai_harvest` module (not loaded if not used)

**Tests:** `tests/test_csi_xai_harvest.py` (22 tests)

All tests mock the API. No network calls in CI.

## Privacy and Data Handling

- API key is read from `XAI_API_KEY` environment variable only
- API key is NEVER logged, printed, or saved to disk
- Raw response JSON is saved for audit (redacted of API key)
- No local caching of responses
- No telemetry beyond cost logging

## See Also

- [Search Handoff Pattern](./search-handoff.md) — How to design harvest prompts
- [xAI API Documentation](https://docs.x.ai/) — Official xAI Responses API docs
- [CSI CLI README](../tools/csi/README.md) — Core CLI reference
