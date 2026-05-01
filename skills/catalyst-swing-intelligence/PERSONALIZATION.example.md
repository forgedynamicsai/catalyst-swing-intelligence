# PERSONALIZATION.example.md
# Copy this file to PERSONALIZATION.local.md and fill in your values.
# PERSONALIZATION.local.md is private — do not publish or commit to a public repo.
# Fields marked [required] must be filled before using the relevant mode.
# Fields marked [optional] improve output quality but have safe defaults.

---

user_profile:
  name: null                          # [optional] Your first name — used in Master Operating Rule
  role_context: null                  # [optional] e.g., "full-time W2 employee, part-time trader"
  timezone: null                      # [optional] e.g., "US/Eastern"
  trading_style: null                 # [optional] e.g., "catalyst-driven swing, 2–12 week holds"

---

## Swing Account

# [required for liquidation-plan mode]
swing_account:
  purpose: "Active swing trading account"
  liquidity_deadline: null            # Hard date by which all positions must be closed
                                      # e.g., "2026-09-01" — fill this in
  no_new_risk_after: null             # Date after which no new positions may be opened
                                      # e.g., "2026-07-01" — typically 60 days before deadline
  max_single_position_weight: 40      # % of account — triggers concentration-check above this
  earnings_hold_policy: null          # e.g., "trim to 20% before any binary earnings event"
  options_allowed: false
  day_trading_allowed: false
  max_active_positions: 5

# [optional] Your current watchlist — helps crowd-scan and next-cycle modes
  current_holdings: []                # e.g., ["MSFT", "NVDA", "VST"]
  candidate_tickers: []               # Tickers on radar but not yet held
  restricted_tickers: []              # Tickers you will not trade (conflict, ethics, etc.)

---

## Long-Horizon Accounts

# [required for long-horizon-account mode]
# Add one entry per account. Remove accounts that don't apply.
long_horizon_accounts:
  - name: null                        # e.g., "Child UTMA"
    beneficiary: null                 # e.g., "child's first name" or role
    account_type: null                # e.g., "UTMA", "529", "Roth IRA"
    target_year: null                 # e.g., 2036
    purpose: null                     # e.g., "college / young adult capital base"
    core_etfs: []                     # e.g., ["SCHD", "QQQ"]
    compounders: []                   # e.g., ["MSFT", "AAPL", "NVDA"]
    turnaround_bets: []               # e.g., ["NKE"] — small, long-horizon
    moonshot_bets: []                 # e.g., ["TSLA"] — call option sizing
    prohibited_behaviors:
      - "applying swing-trading logic"
      - "adding to turnaround positions without evidence improvement"
      - "concentration above 40% in any single name"

---

## Personal Rules

# [optional] Rules that override or supplement the public skill defaults.
# State each as a hard rule that can be evaluated as pass/fail.
personal_rules:
  - null
  # Examples:
  # - "No new positions within 30 days of liquidity deadline"
  # - "Hold TICKER_A through any catalyst in the hold window"
  # - "Never add to a losing position without a new thesis data point"

---

## Master Operating Rule (Personalized)

# [optional] Replace the generic version in SKILL.md with your version.
# Leave null to use the generic version.
master_operating_rule: null
# Example:
# master_operating_rule: |
#   For [child name]'s account, compound.
#   For [your name]'s account, swing.
#   Never apply short-term swing logic to long-term capital.

---

## Output Preferences

output_preferences:
  preferred_format: markdown
  include_tables: true
  include_decision: true
  include_risk_disclosure: true
  include_tax_note: false             # Set to true if tax efficiency is a regular concern
