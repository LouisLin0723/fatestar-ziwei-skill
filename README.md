# FateStar Ziwei

Zi Wei Dou Shu (Purple Star Astrology) for AI agents. Install one Agent Skill, connect one hosted MCP endpoint, or call the free REST API.

[简体中文](./README.zh-CN.md)

[![Validate](https://github.com/LouisLin0723/fatestar-ziwei/actions/workflows/validate.yml/badge.svg)](https://github.com/LouisLin0723/fatestar-ziwei/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/LouisLin0723/fatestar-ziwei)](https://github.com/LouisLin0723/fatestar-ziwei/releases)
[![Stars](https://img.shields.io/github/stars/LouisLin0723/fatestar-ziwei?style=flat)](https://github.com/LouisLin0723/fatestar-ziwei/stargazers)
[![License](https://img.shields.io/github/license/LouisLin0723/fatestar-ziwei)](./LICENSE)

Charting and six-level transits are free and can be used anonymously. The optional Zheng Da Qian reading uses a FateStar API key and credits.

If this project saves you setup time, [star the repository](https://github.com/LouisLin0723/fatestar-ziwei). It helps other agent users find it.

## See it work

After installing the Skill, tell your agent:

> Create a Zi Wei Dou Shu chart for a man born on July 23, 1990 at 8:00 AM, then show his 2026 transits.

The agent calls FateStar and returns:

- a natal chart with 12 palaces, stars, brightness, and Four Transformations;
- true-solar-time correction when longitude and timezone are supplied;
- decade, annual, monthly, daily, and hourly transits;
- an optional Zheng Da Qian reading when a valid key and credits are available.

## Quick start

### Agent Skill

GitHub CLI 2.90 or newer installs the Skill into Codex, Claude Code, Cursor, and many other agents.

```bash
# Codex
gh skill install LouisLin0723/fatestar-ziwei ziwei-paipan --agent codex --scope user

# Claude Code
gh skill install LouisLin0723/fatestar-ziwei ziwei-paipan --agent claude-code --scope user

# Cursor
gh skill install LouisLin0723/fatestar-ziwei ziwei-paipan --agent cursor --scope user
```

Restart the agent, then ask it to create a Zi Wei Dou Shu chart. The canonical Skill is in [`skills/ziwei-paipan`](./skills/ziwei-paipan).

If your GitHub CLI is older, [upgrade it](https://github.com/cli/cli#installation) or copy the `skills/ziwei-paipan` directory into your agent's Skill directory.

### Hosted MCP

No local server is required. Add the remote endpoint to a client that supports Streamable HTTP:

```jsonc
{
  "mcpServers": {
    "fatestar-ziwei": {
      "url": "https://www.fatestar.top/api/mcp"
    }
  }
}
```

The endpoint exposes `ziwei_chart`, `ziwei_transits`, and `ziwei_reading`. The first two tools are free and anonymous.

### REST API

Run a free chart request without an account:

```bash
curl "https://www.fatestar.top/api/ziwei?year=1990&month=7&day=23&hour=8&gender=male"
```

Full API and client documentation: [fatestar.top/docs](https://www.fatestar.top/docs)

## Choose an integration

| Integration | Best for | Install | Free charting |
| --- | --- | --- | --- |
| Agent Skill | Codex, Claude Code, Cursor, and other coding agents | `gh skill install` | Yes |
| Hosted MCP | MCP clients with remote HTTP support | One URL | Yes |
| REST API | Apps, scripts, and backend services | `curl` or HTTP client | Yes |

All three routes use the same FateStar engine. Pick the interface that fits your client.

## Capabilities

| Capability | Cost | Notes |
| --- | --- | --- |
| Natal chart | Free | Solar or lunar input, 12 palaces, 102 stars, brightness, Four Transformations |
| Six-level transits | Free | Decade, minor cycle, year, month, day, and hour |
| True solar time | Free | Enabled with longitude and timezone input |
| Zheng Da Qian reading | Credits | FateStar knowledge engine and hosted reading service |

The Skill ships Python, Node.js, PowerShell, and Bash clients. Python and Node.js use their standard libraries and require no package install.

## CLI examples

Run these commands from the installed `ziwei-paipan` Skill directory:

```bash
# Free natal chart
python scripts/ziwei_cli.py chart \
  --year 1990 --month 7 --day 23 --hour 8 --gender male

# Free 2026 transits
python scripts/ziwei_cli.py transits \
  --year 1990 --month 7 --day 23 --hour 8 --gender male \
  --target-year 2026

# Hosted reading, requires FATESTAR_API_KEY
python scripts/ziwei_cli.py reading \
  --year 1990 --month 7 --day 23 --hour 8 --gender male \
  --question "Should I change jobs this year?"
```

Use `python scripts/ziwei_cli.py doc` for the offline interface reference. Equivalent Node.js, PowerShell, and Bash clients are in the same directory.

## API key and billing

`chart` and `transits` are free with or without a key. A key only attributes those free calls to your account.

`reading` requires an `FSFSKey` and may consume credits. Create a key in the [FateStar developer center](https://www.fatestar.top/finance/developer). Store it outside source control:

```bash
export FATESTAR_API_KEY="FSFSKey_your_key"
```

For MCP clients, send `Authorization: Bearer FSFSKey_your_key` only when you want to use `ziwei_reading`. Never commit a real key or paste it into an issue.

## Repository layout

```text
skills/ziwei-paipan/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── ziwei_cli.py
│   ├── ziwei_cli.js
│   ├── ziwei_cli.ps1
│   ├── ziwei_cli.sh
│   └── shared/
```

The root [`server.json`](./server.json) describes the hosted endpoint using the official MCP Registry schema.

## Development

```bash
python skills/ziwei-paipan/scripts/generate.py --check
python skills/ziwei-paipan/scripts/ziwei_cli.py doc
node skills/ziwei-paipan/scripts/ziwei_cli.js doc
powershell -ExecutionPolicy Bypass -File skills/ziwei-paipan/scripts/ziwei_cli.ps1 doc
bash skills/ziwei-paipan/scripts/ziwei_cli.sh doc
```

The four clients share generated constants and an offline interface spec. Edit the shared files first, run `generate.py`, then run the checks above.
The broader compatibility matrix is in [`docs/TEST_PLAN.md`](./docs/TEST_PLAN.md).

## Open-source boundary

This repository contains the Agent Skill, four thin clients, integration metadata, and public documentation. FateStar's server implementation, private prompts, Zheng Da Qian training data, retrieval corpus, evaluation sets, and billing controls are not included.

The repository code is MIT licensed. FateStar's brand, hosted service, and private knowledge assets remain proprietary.

## Contributing

Bug reports, client examples, and compatibility fixes are welcome. Read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a pull request. Security reports belong in [SECURITY.md](./SECURITY.md), not a public issue.
