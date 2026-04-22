# AgentScan

AgentScan is a deterministic Python CLI that scans AI agent artifacts (such as prompt/config YAML and Markdown files) for high-signal risky patterns.

## What it does

- Discovers supported agent artifacts in a target directory.
- Parses artifacts into normalized content.
- Applies built-in YAML rules and regex matchers.
- Produces deterministic findings for CI-friendly checks.

## Install

```bash
python3 -m pip install -e '.[dev]'
```

## Quick start

Scan a directory:

```bash
agentscan scan tests/fixtures/safe
```

Useful examples:

```bash
agentscan scan tests/fixtures/unsafe
agentscan scan tests/fixtures/empty
```

## Run tests

```bash
python3 -m pytest tests -v
```

## Project layout

- `src/agentscan/` – scanner implementation
- `src/agentscan/builtin_rules/` – built-in rule definitions
- `tests/` – unit and integration tests with fixtures
- `docs/superpowers/specs/` – design specs
- `docs/superpowers/plans/` – implementation plans

## Notes

- Behavior is designed to be deterministic and stable across runs.
- See `AgentScan_SRS_v1.0.md` for product requirements and milestone context.
