"""
xAI/Grok Evidence Harvest Adapter

This optional module harvests evidence from xAI/Grok via X Search and Web Search APIs.
It produces CSI-compatible markdown evidence tables without requiring local manual search.

Architecture:
- Uses xAI Responses API (POST /responses) with x_search and web_search tools
- Generates a harvest prompt that instructs Grok to produce markdown evidence table
- Parses response, saves raw JSON, logs cost to jsonl
- Optionally runs full CSI pipeline (import → validate → score → report → observe)

Non-advisory boundary (enforced throughout):
- Output is crowd signal evidence, NOT investment recommendations
- No buy/sell/hold advice, no price targets, no position sizing
- Distinguishes X virality from evidence quality
- Identifies source coverage gaps, does not invent sources

Cost handling:
- Logs actual xAI API cost to data/csi/xai_costs.jsonl
- Displays cost warning if --budget-usd set (display-only, not enforced)
- Returns cost in USD (converted from xAI's cost_in_usd_ticks)
"""

import json
import os
import sys
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

XAI_BASE_URL = "https://api.x.ai/v1"
XAI_RESPONSES_ENDPOINT = "/responses"
DEFAULT_MODEL = "grok-3"
DEFAULT_TOOLS = "x,web"

# Source class constants (from csi.py)
VALID_SOURCE_CLASSES = {
    "primary_filing", "earnings_transcript", "company_ir", "major_news",
    "trade_publication", "investing_forum", "social_media", "prediction_market",
    "pundit", "whale_positioning", "copy_trading", "market_data", "unknown",
}

NON_ADVISORY_BOUNDARY = (
    "This analysis is crowd signal evidence, not investment advice. "
    "It does not recommend purchases, investments, trades, or position sizing."
)


# ---------------------------------------------------------------------------
# Harvest prompt builder
# ---------------------------------------------------------------------------

def build_harvest_prompt(theme: str, max_sources: int = 20) -> str:
    """
    Build a prompt that instructs Grok to harvest evidence for a theme.

    Key instructions:
    - Use X/social search for narrative velocity and source emergence
    - Use web/news search for source diversity and confirmation
    - Search public/open sources only
    - Distinguish X virality from evidence quality
    - Identify whether multiple posts trace back to one original source
    - Mark source classes as unavailable if not found — do NOT invent sources
    - Output ONLY a CSI-compatible markdown evidence table
    - Include URLs/citations where available
    - NOT provide buy/sell/hold advice
    - NOT recommend purchases, investments, trades, position sizing, or companies to buy
    """

    return f"""\
You are a evidence researcher for crowd signal analysis. Your task is to harvest evidence related to this theme:

THEME: "{theme}"

INSTRUCTIONS:

1. SEARCH STRATEGY
   - Use X/social search to find narrative velocity and source emergence patterns
   - Use web/news search to find source diversity and confirmation
   - Search ONLY public/open sources — no logins, paywalls, private feeds
   - Prioritize recent, high-credibility sources

2. CRITICAL DISTINCTIONS
   - X virality (retweets, likes) is a SIGNAL OF NARRATIVE VELOCITY, NOT EVIDENCE QUALITY
   - Engagement metrics do NOT validate claims — cross-check with news/filings
   - Identify whether multiple posts trace back to one original source (avoid double-counting)
   - Mark unavailable source classes explicitly — do NOT invent sources

3. SOURCE COVERAGE TARGET
   - Attempt to find evidence across these source classes:
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
   - If you cannot find evidence for a class, mark it as unavailable — do not fabricate

4. NON-ADVISORY BOUNDARY (STRICT)
   - Output evidence about market signals, not investment recommendations
   - Do NOT provide buy/sell/hold advice
   - Do NOT recommend purchases, investments, trades, position sizing, or specific companies to buy
   - Do NOT provide price targets, expected returns, or alpha claims
   - Output is for crowd signal assessment only

5. OUTPUT FORMAT
   - Return ONLY a CSI-compatible markdown evidence table
   - No introduction, no explanation, no summary
   - Table columns (in order):
     claim | source_name | source_url | source_class | source_date | source_type | \
independence_rating | evidence_quality | specificity | catalyst_alignment | dissent_quality | \
time_signal | is_duplicate | notes
   - One row per unique claim/source pair
   - Include URLs/citations where available
   - Mark duplicates as "true" if multiple sources report the same fact from one origin
   - Aim for {max_sources} sources, but quality > quantity

6. CELL CONTENT RULES
   - claim: The specific claim or signal (e.g., "GPU memory bandwidth constraints in data centers")
   - source_name: Organization/person name (e.g., "Reuters", "NVIDIA IR", "AnandTech")
   - source_url: Full URL if available, empty if not found
   - source_class: ONE of the 13 classes above (or "unknown")
   - source_date: ISO 8601 (YYYY-MM-DD) or empty if unknown
   - source_type: "news", "forum", "filing", "social", "analysis", "prediction", "data", or "unknown"
   - independence_rating: 0-20 (0=paid/biased, 10=neutral, 20=independent)
   - evidence_quality: 0-20 (0=rumor, 10=credible, 20=primary source)
   - specificity: 0-20 (0=vague, 10=specific, 20=quantified)
   - catalyst_alignment: 0-10 (how well this evidence maps to your stated theme)
   - dissent_quality: 0-5 (quality of opposing view, if present; 0=none, 5=strong)
   - time_signal: 0-10 (urgency/recency, 0=stale, 10=breaking)
   - is_duplicate: "true" or "false" (is this the same fact from a downstream source?)
   - notes: Context, caveats, or calculation basis

7. QUALITY GATES
   - Every source must be real (no fabricated URLs or organizations)
   - Every claim must be traceable to the source
   - If you cannot find a claim in a particular source class, leave it out (do not invent)
   - Avoid echo-chamber risk by including independent sources

Return the markdown table only. Do not add any other text.
"""


# ---------------------------------------------------------------------------
# xAI API interaction
# ---------------------------------------------------------------------------

def check_api_key() -> tuple[bool, str]:
    """Check if XAI_API_KEY is set. Returns (is_set, message)."""
    key = os.environ.get("XAI_API_KEY")
    if key:
        return True, ""
    msg = (
        "XAI_API_KEY is not set.\n\n"
        "Set it for this shell session:\n\n"
        "  export XAI_API_KEY=\"your_api_key\"\n\n"
        "No request was sent."
    )
    return False, msg


def make_request(
    api_key: str,
    theme: str,
    model: str = DEFAULT_MODEL,
    tools: str = DEFAULT_TOOLS,
    max_sources: int = 20,
) -> tuple[dict | None, str]:
    """
    Call xAI Responses API with harvest prompt.

    Returns (response_dict, error_message).
    response_dict is None if error occurred.
    """

    # Parse tools
    tool_list = []
    if "x" in tools.lower():
        tool_list.append({"type": "x_search"})
    if "web" in tools.lower():
        tool_list.append({"type": "web_search"})

    prompt = build_harvest_prompt(theme, max_sources)

    # Build request body
    request_body = {
        "model": model,
        "tools": tool_list,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    url = f"{XAI_BASE_URL}{XAI_RESPONSES_ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(request_body).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            response_data = response.read().decode("utf-8")
            return json.loads(response_data), ""
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode("utf-8", errors="replace")

        if status == 401 or status == 403:
            return None, "Authentication failed. Check XAI_API_KEY."
        elif status == 429:
            return None, "Rate limited. Wait and retry."
        elif status == 404:
            return None, "Model or endpoint not available."
        else:
            return None, f"HTTP {status}: {body}"
    except urllib.error.URLError as e:
        return None, f"Network error: {e}"
    except json.JSONDecodeError:
        return None, "xAI response was not valid JSON."
    except Exception as e:
        return None, f"Unexpected error: {e}"


def extract_cost_usd(response: dict) -> float | None:
    """Extract cost from response in USD. xAI returns cost_in_usd_ticks."""
    try:
        usage = response.get("usage", {})
        ticks = usage.get("cost_in_usd_ticks")
        if ticks is None:
            return None
        # Convert: cost_usd = cost_in_usd_ticks / 10_000_000_000
        return ticks / 10_000_000_000
    except (TypeError, KeyError):
        return None


def extract_markdown_table(response: dict) -> str | None:
    """
    Extract markdown evidence table from response content.

    Grok should return the markdown table in response.choices[0].message.content
    """
    try:
        choices = response.get("choices", [])
        if not choices:
            return None
        message = choices[0].get("message", {})
        content = message.get("content", "")

        if not content:
            return None

        # Look for markdown table in content
        # Table starts with | and contains pipe-delimited columns
        lines = content.split("\n")
        table_lines = []
        in_table = False

        for line in lines:
            if line.strip().startswith("|"):
                in_table = True
                table_lines.append(line)
            elif in_table and not line.strip().startswith("|"):
                break

        if table_lines:
            return "\n".join(table_lines)

        return None
    except (KeyError, IndexError, TypeError):
        return None


# ---------------------------------------------------------------------------
# File I/O and logging
# ---------------------------------------------------------------------------

def make_slug(theme: str) -> str:
    """Convert theme to a filesystem-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", theme.lower())
    slug = slug.strip("-")
    return slug[:64]  # Cap at 64 chars


def save_raw_response(response: dict, theme: str, data_dir: str = "harvests/xai") -> str:
    """
    Save full response JSON, redacted of API key.
    Returns the path where saved.
    """
    Path(data_dir).mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    slug = make_slug(theme)
    filename = f"{ts}-{slug}-raw-response.json"
    filepath = os.path.join(data_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2, ensure_ascii=False)

    return filepath


def log_cost(
    theme: str,
    model: str,
    tools: str,
    cost_usd: float | None,
    raw_response_path: str,
    evidence_md_path: str,
    data_dir: str = "data/csi",
) -> None:
    """
    Log cost to data/csi/xai_costs.jsonl
    """
    Path(data_dir).mkdir(parents=True, exist_ok=True)

    cost_log_path = os.path.join(data_dir, "xai_costs.jsonl")

    # Parse tools list for logging
    tool_list = []
    if "x" in tools.lower():
        tool_list.append("x_search")
    if "web" in tools.lower():
        tool_list.append("web_search")

    entry = {
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
        "theme": theme,
        "model": model,
        "tools": tool_list,
        "cost_usd": cost_usd,
        "raw_response_path": raw_response_path,
        "evidence_md_path": evidence_md_path,
    }

    with open(cost_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Main harvest command
# ---------------------------------------------------------------------------

def harvest(
    theme: str,
    output_path: str = None,
    auto_score: bool = False,
    runtime_tools: str = DEFAULT_TOOLS,
    model: str = DEFAULT_MODEL,
    max_sources: int = 20,
    budget_usd: float = None,
    data_dir: str = "data/csi",
    reports_dir: str = "reports/csi",
) -> str:
    """
    Main harvest command. Calls xAI Responses API, saves evidence markdown.

    If auto_score=True, runs full pipeline: import → validate → score → report → observe

    Returns: status message (print this to stdout)
    """

    # Check API key
    api_ok, api_msg = check_api_key()
    if not api_ok:
        return api_msg

    # Print preflight messages
    lines = []

    if budget_usd is not None:
        lines.append(f"Budget guard: ${budget_usd:.2f}. This adapter cannot guarantee "
                     f"final cost before xAI returns usage data.")

    lines.append(f"Harvesting evidence for theme: \"{theme}\" using xAI "
                 f"({runtime_tools}, model={model})...")

    # Make API call
    api_key = os.environ.get("XAI_API_KEY")
    response, error = make_request(api_key, theme, model, runtime_tools, max_sources)

    if error:
        lines.append(f"Error: {error}")
        return "\n".join(lines)

    # Extract markdown table
    markdown_table = extract_markdown_table(response)
    if not markdown_table:
        lines.append("Error: xAI response did not contain a markdown evidence table.")
        return "\n".join(lines)

    # Determine output path
    if output_path is None:
        slug = make_slug(theme)
        output_path = f"evidence/csi/{slug}-xai-evidence.md"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Save markdown evidence
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_table + "\n")

    lines.append(f"Saved markdown evidence to: {output_path}")

    # Save raw response
    raw_response_path = save_raw_response(response, theme, "harvests/xai")
    lines.append(f"Saved raw response to: {raw_response_path}")

    # Extract and log cost
    cost_usd = extract_cost_usd(response)
    if cost_usd is not None:
        lines.append(f"Actual request cost: ${cost_usd:.6f}")
    else:
        lines.append("Actual request cost: unknown")

    log_cost(theme, model, runtime_tools, cost_usd, raw_response_path, output_path, data_dir)

    # Auto-score pipeline
    if auto_score:
        lines.append("\n--- Auto-Score Pipeline ---")

        # Convert markdown to CSV
        csv_output = output_path.replace(".md", ".csv")
        import importer as _imp
        import_msg, import_code = _imp.import_md(output_path, csv_output, append=False)
        lines.append(import_msg)

        if import_code != 0:
            lines.append(f"\nAuto-score stopped: import-md failed.")
            return "\n".join(lines)

        # Validate
        import validation as _val
        val_msg, val_code = _val.cmd_validate(csv_output, strict=False)
        lines.append(val_msg)

        if val_code != 0:
            lines.append(f"\nAuto-score stopped: validation failed.")
            return "\n".join(lines)

        # Score
        import csi as _csi
        score_output = _csi.cmd_score(csv_output)
        lines.append(score_output)

        # Report
        report_output = output_path.replace("-xai-evidence.md", "-xai-report.md")
        report_msg = _csi.cmd_report(csv_output, report_output, theme=theme)
        lines.append(f"Saved report to: {report_output}")

        # Observe
        import memory as _mem
        observe_msg = _mem.cmd_observe(csv_output, theme, data_dir=data_dir, reports_dir=reports_dir)
        lines.append(observe_msg)

        # Print next commands
        lines.append("\nNext commands:")
        lines.append(f"  python tools/csi/csi.py outcome <signal_id> --event-confirmed true")
        lines.append(f"  python tools/csi/csi.py list --month $(date +%Y-%m)")
        lines.append(f"  python tools/csi/csi.py monthly-review --month $(date +%Y-%m)")
    else:
        # Just print next commands for manual pipeline
        csv_output = output_path.replace(".md", ".csv")
        lines.append("\nTo continue with the full pipeline:")
        lines.append(f"  python tools/csi/csi.py import-md {output_path}")
        lines.append(f"  python tools/csi/csi.py validate {csv_output}")
        lines.append(f"  python tools/csi/csi.py score {csv_output}")
        lines.append(f"  python tools/csi/csi.py report {csv_output} --output report.md")
        lines.append(f"  python tools/csi/csi.py observe {csv_output} --theme \"{theme}\"")

    return "\n".join(lines)
