---
name: ziwei-paipan
description: Use FateStar to create free Zi Wei Dou Shu natal charts and six-level transit data, with optional paid Zheng Da Qian readings only after explicit user confirmation. Trigger for 紫微斗数、紫微命盘、排盘、流年、运限、Purple Star Astrology, or birth-chart questions when birth date, hour, and gender can be collected.
---

# FateStar Ziwei

Use the bundled CLI to request deterministic Zi Wei Dou Shu chart data from FateStar. Keep free charting separate from the optional paid reading service.

## Choose the operation

- Use `chart` for a natal chart. It is free and works anonymously.
- Use `transits` for decade, minor-cycle, annual, monthly, daily, and hourly transit data. It is free and works anonymously.
- Offer `reading` only when the user wants the hosted Zheng Da Qian interpretation. It requires an `FSFSKey` and may consume credits.

Never call `reading`, or any other paid endpoint, until the user explicitly chooses it and acknowledges that credits may be consumed. A request such as “看事业运” is not consent to spend credits: use the free chart data first, then offer the paid reading as an option.

## Collect input

Require these fields and ask for any that are missing. Do not guess them:

- birth year, month, and day;
- birth hour from `0` to `23`;
- gender: `male` or `female`.

Use `solar` as the calendar unless the user says the date is lunar. Accept birth minute, longitude, and timezone when the user wants true-solar-time correction.

## Run the CLI

Treat the directory containing this file as `<skill_dir>`. Prefer Python, then Node.js, then the platform shell:

- Python 3.6+: `python <skill_dir>/scripts/ziwei_cli.py`
- Node.js 12+: `node <skill_dir>/scripts/ziwei_cli.js`
- Windows PowerShell 5.1+: `powershell -ExecutionPolicy Bypass -File <skill_dir>/scripts/ziwei_cli.ps1`
- Bash 4+ with curl: `bash <skill_dir>/scripts/ziwei_cli.sh`

If `<skill_dir>/runtime.conf` exists, follow its configured runtime and command. Run `<cmd> doc` for the complete offline parameter reference.

```bash
# Free natal chart
<cmd> chart --year 1990 --month 7 --day 23 --hour 8 --gender male

# Free transits for 2026
<cmd> transits --year 1990 --month 7 --day 23 --hour 8 --gender male --target-year 2026

# Optional hosted reading; confirm possible credit use first
<cmd> reading --year 1990 --month 7 --day 23 --hour 8 --gender male --question "Should I change jobs this year?"
```

## Handle keys and failures

Read the key from `FATESTAR_API_KEY`, a local `.env`, or the explicit `--api_key` argument. Never print, quote back, log, or persist a real key. Recommend environment configuration if the user pasted a key into chat.

The CLI sends `X-FateStar-Client: skill/2.2.0`. A key on `chart` or `transits` only attributes the free request; it does not make those operations paid.

- On `401`, stop and ask the user to verify or replace the key.
- On `402`, do not retry the paid request. Report that credits are insufficient and offer the free chart workflow.
- On timeouts or `5xx` errors, report the failure without inventing chart data.

## Interpret safely

Preserve the returned chart fields and distinguish the two stem-branch systems in transit output:

- Use the real calendar stem-branch value when discussing dates.
- Use the palace stem-branch value only for palace and Four Transformation calculations.

Do not present astrology as certain fact or as a substitute for professional medical, legal, or financial advice. Do not save birth data or chart results unless the user explicitly asks and the active product provides an appropriate storage action.

For remote MCP and REST integration details, use <https://www.fatestar.top/docs>.
