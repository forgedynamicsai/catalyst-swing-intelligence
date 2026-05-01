# Personalization Pattern

This skill uses a public/private overlay pattern to separate reusable methodology
from user-specific context.

---

## The Three Files

### `SKILL.md` — Public methodology

Contains only reusable logic: modes, decision trees, scoring rubrics, output
contracts, quality checklists, and guardrails.

Safe to publish. Safe to share. A stranger can use it without modification.

Does not contain: names, account details, holdings, deadlines, or personal rules.

### `PERSONALIZATION.example.md` — Public template

A YAML template showing every field a user can customize. All values are null or
empty. Comments show example values using generic placeholders.

Safe to publish. Serves as documentation for what the personalization layer supports.

### `PERSONALIZATION.local.md` — Private user config

Your filled-in copy of the example template. Contains your accounts, deadlines,
holdings, and personal rules.

**Never publish this file. Treat it like a `.env` file.**

It is gitignored by default. Do not override this.

---

## How the Skill Uses Personalization

When a mode like `long-horizon-account` or `liquidation-plan` fires, the skill
instructs the model to check `PERSONALIZATION.local.md` for user-specific defaults
(account names, deadlines, holdings, personal rules).

If the file does not exist, the skill falls back to generic prompts and asks the
user to supply the missing context inline.

---

## Updating Your Private Config

Update `PERSONALIZATION.local.md` when:

- Your holdings change materially
- Your liquidity deadline changes
- You open a new long-horizon account
- You add a new personal rule after a hard lesson

You do not need to update `SKILL.md` for any of these changes.

---

## Contributing a New Mode

If you build a new mode and want to contribute it:

1. Add the mode to `SKILL.md` using generic language only.
2. If the mode needs user-specific defaults, add the corresponding fields to
   `PERSONALIZATION.example.md` with null values and illustrative comments.
3. Do not add filled-in values to `PERSONALIZATION.example.md`.
4. Do not reference specific tickers, account names, or personal rules in `SKILL.md`.
