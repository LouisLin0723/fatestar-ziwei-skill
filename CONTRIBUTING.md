# Contributing

Contributions should make FateStar easier to install, call, or verify without exposing private service internals.

## Good contributions

- reproducible client compatibility fixes;
- clearer installation steps for supported agents;
- tests for the four CLI clients;
- examples that use the public Skill, MCP, or REST interfaces;
- documentation corrections backed by a working request.

## Before opening a pull request

Run:

```bash
python skills/ziwei-paipan/scripts/generate.py --check
python skills/ziwei-paipan/scripts/ziwei_cli.py doc
node skills/ziwei-paipan/scripts/ziwei_cli.js doc
bash skills/ziwei-paipan/scripts/ziwei_cli.sh doc
```

On Windows, also run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File skills/ziwei-paipan/scripts/ziwei_cli.ps1 doc
```

Do not commit API keys, private prompts, production data, user birth data, or generated readings. Report security issues through [SECURITY.md](./SECURITY.md).
