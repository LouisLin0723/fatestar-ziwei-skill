# FateStar Ziwei

A Zi Wei-focused hosted MCP for AI agents. One URL; no local server, package install, account, or API key for natal charts and six transit levels. Also available as an Agent Skill and REST API.

[简体中文](./README.zh-CN.md)

[![Validate](https://github.com/LouisLin0723/fatestar-ziwei/actions/workflows/validate.yml/badge.svg)](https://github.com/LouisLin0723/fatestar-ziwei/actions/workflows/validate.yml)
[![Live contract](https://github.com/LouisLin0723/fatestar-ziwei/actions/workflows/live-contract.yml/badge.svg)](https://github.com/LouisLin0723/fatestar-ziwei/actions/workflows/live-contract.yml)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-listed-8b5cf6)](https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.LouisLin0723%2Ffatestar-ziwei)
[![Release](https://img.shields.io/github/v/release/LouisLin0723/fatestar-ziwei)](https://github.com/LouisLin0723/fatestar-ziwei/releases)
[![Stars](https://img.shields.io/github/stars/LouisLin0723/fatestar-ziwei?style=flat)](https://github.com/LouisLin0723/fatestar-ziwei/stargazers)
[![License](https://img.shields.io/github/license/LouisLin0723/fatestar-ziwei)](./LICENSE)

![FateStar Ziwei Agent Skill, hosted MCP, and REST API preview](./assets/fatestar-ziwei-social-preview.png)

Natal charts and six-level transits work anonymously. The optional Zheng Da Qian reading uses a FateStar API key and credits.

## Try it now

[Open a live anonymous chart response](https://www.fatestar.top/api/ziwei?year=1990&month=7&day=23&hour=8&gender=male). No account or API key is required. Selected fields from that response:

```text
Solar 1990-7-23 | Lunar 一九九〇年六月初二
Five-elements class 土五局 | Life ruler 文曲 | Body ruler 火星
Life palace 己卯 | 廉贞 (平), 破军 (陷)
12 palaces | 5 detected patterns | 4 natal transformations
```

After installing the Skill or connecting the MCP endpoint, tell your agent:

> Create a Zi Wei Dou Shu chart for a man born on July 23, 1990 at 8:00 AM, then show his 2026 transits.

The agent calls FateStar and returns:

- a natal chart with 12 palaces, stars, brightness, and Four Transformations;
- true-solar-time correction when longitude and timezone are supplied;
- decade, minor-cycle, annual, monthly, daily, and hourly transits;
- an optional Zheng Da Qian reading when a valid key and credits are available.

If the live result is useful, [star the repository](https://github.com/LouisLin0723/fatestar-ziwei). It helps other agent developers find the free endpoint.

## Why FateStar

FateStar is deliberately narrow: it makes Zi Wei chart data easy to use from an AI agent without operating a local astrology server.

| Choose | When it fits |
| --- | --- |
| **FateStar** | You want a hosted remote MCP now: one URL, anonymous free charting, six transit levels, native structured MCP output, and an official Registry listing. |
| [Iztro](https://github.com/SylarLong/iztro) | You need an open-source Zi Wei engine to embed, inspect, or modify inside your own application. |
| [Taibu](https://github.com/hhszzzz/taibu) or [Horosa Skill](https://github.com/Horace-Maxwell/horosa-skill) | You prefer broader multi-system or offline metaphysics tooling over a focused hosted Zi Wei endpoint. |

These are different deployment choices, not a claim that one school or engine is universally more accurate.

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

`tools/list` declares an `outputSchema` and behavior annotations for every tool. Successful calls return both native `structuredContent` and legacy JSON text, so newer agents can consume typed fields while older clients keep working.

The server is listed in the official MCP Registry as [`io.github.LouisLin0723/fatestar-ziwei`](https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.LouisLin0723%2Ffatestar-ziwei).

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
python tests/live_contract_check.py
python skills/ziwei-paipan/scripts/ziwei_cli.py doc
node skills/ziwei-paipan/scripts/ziwei_cli.js doc
powershell -ExecutionPolicy Bypass -File skills/ziwei-paipan/scripts/ziwei_cli.ps1 doc
bash skills/ziwei-paipan/scripts/ziwei_cli.sh doc
```

The four clients share generated constants and an offline interface spec. Edit the shared files first, run `generate.py`, then run the checks above.
The broader compatibility matrix is in [`docs/TEST_PLAN.md`](./docs/TEST_PLAN.md). The exact hosted MCP assertions and their limits are documented in [`docs/VERIFICATION.md`](./docs/VERIFICATION.md).

## Open-source boundary

This repository contains the Agent Skill, four thin clients, integration metadata, and public documentation. FateStar's server implementation, private prompts, Zheng Da Qian training data, retrieval corpus, evaluation sets, and billing controls are not included.

The repository code is MIT licensed. FateStar's brand, hosted service, and private knowledge assets remain proprietary.

## Contributing

Bug reports, client examples, and compatibility fixes are welcome. Read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a pull request. Security reports belong in [SECURITY.md](./SECURITY.md), not a public issue.
