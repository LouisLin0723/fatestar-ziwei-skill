# Verification

FateStar publishes two different kinds of automated evidence.

## Repository validation

`.github/workflows/validate.yml` checks the Skill layout, generated-client consistency, syntax, CLI help, offline documentation, and MCP Registry metadata on Linux and Windows.

Run it locally:

```bash
python skills/ziwei-paipan/scripts/generate.py --check
```

## Hosted MCP contract

`.github/workflows/live-contract.yml` calls the public anonymous endpoint on a schedule and on manual dispatch:

```bash
python tests/live_contract_check.py
```

The script verifies:

- MCP initialization and the advertised protocol version;
- the exact three-tool inventory;
- `outputSchema` and behavior annotations;
- equality between native `structuredContent` and legacy JSON text;
- a fixed natal-chart regression case with 12 palaces and Four Transformations;
- the presence of all six transit levels for a fixed target date.

Set `FATESTAR_MCP_URL` to test another deployment, for example a local preview.

The check never calls `ziwei_reading`, so it does not use an API key or paid credits. It validates transport and deterministic regression fixtures; it is not proof of universal metaphysical accuracy, a comparison of schools, or an AI-reading quality benchmark.
