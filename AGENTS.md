# AGENTS.md

## Purpose

This repository is a small, deterministic Python CLI scanner for AI agent artifacts.
Optimize for correctness, tight scope control, and fast verification.

Work as a Codex coding agent, not as a general brainstorming assistant, unless the user explicitly asks for design or planning.

## Repo Layout

- `src/agentscan/`: scanner implementation
- `src/agentscan/builtin_rules/`: declarative builtin rule YAML files
- `tests/`: unit, integration, and fixture-based coverage
- `docs/superpowers/specs/`: design docs
- `docs/superpowers/plans/`: implementation plans
- `AgentScan_SRS_v1.0.md`: product requirements and milestone reference

## Environment

Use Python 3 only.

Preferred setup:

```bash
python3 -m pip install -e '.[dev]'
```

If working in Codex cloud, prefer an environment that:

- uses the `universal` base image
- pins Python to `3.13`
- runs `python3 -m pip install -e '.[dev]'` in setup
- keeps agent internet access off unless the task explicitly needs it

## Core Commands

Install dependencies:

```bash
python3 -m pip install -e '.[dev]'
```

Run the full test suite:

```bash
python3 -m pytest tests -v
```

Run representative CLI checks:

```bash
agentscan scan tests/fixtures/safe
agentscan scan tests/fixtures/unsafe
agentscan scan tests/fixtures/empty
```

## Working Rules

- Write the test first for any feature, bugfix, or behavior change.
- Keep changes small and local. Follow the existing module boundaries.
- Do not silently expand scope from the current milestone to later milestones.
- Preserve deterministic behavior. Stable ordering and reproducible output matter.
- Prefer `rg` and `rg --files` for search.
- Avoid adding dependencies unless the user asked for it or the repo clearly needs it.
- Do not rewrite or normalize fixture contents unless the test explicitly requires it.
  In particular, preserve the real zero-width character in `tests/fixtures/unsafe/zero_width_prompt.md`.

## Rule And Scanner Changes

If you touch any of these:

- `src/agentscan/matchers.py`
- `src/agentscan/parser.py`
- `src/agentscan/rules.py`
- `src/agentscan/reporting.py`
- `src/agentscan/scanner.py`
- `src/agentscan/builtin_rules/*.yml`

Then run, at minimum:

```bash
python3 -m pytest tests -v
agentscan scan tests/fixtures/safe
agentscan scan tests/fixtures/unsafe
agentscan scan tests/fixtures/empty
```

## Git Workflow

- Do not do non-trivial work directly on `main`.
- Prefer a dedicated branch or git worktree for feature work.
- Make small, logical commits.
- Never use destructive commands like `git reset --hard` or `git checkout --` unless the user explicitly asks for them.
- Do not revert unrelated user changes.

## Verification

Do not claim work is done, fixed, or passing until you have run the relevant verification commands again.

Default verification for code changes:

```bash
python3 -m pytest tests -v
```

Extra verification for CLI, reporting, discovery, or rule changes:

```bash
agentscan scan tests/fixtures/safe
agentscan scan tests/fixtures/unsafe
agentscan scan tests/fixtures/empty
```

If you only changed documentation, verify at least with:

```bash
git diff --check
```

## Task Execution Norms

- If the user asks for a change, implement it instead of only describing it.
- If you hit a real blocker, say exactly what the blocker is.
- If code, tests, and docs disagree, surface the mismatch and choose the least disruptive path unless the user says otherwise.
- When reviewing code, prioritize bugs, regressions, edge cases, and missing tests.
- Keep responses concise and concrete.

## Out Of Scope By Default

Do not introduce these unless the user explicitly asks for them:

- semantic or embedding-based detection
- LLM judge integration
- provider-aware auto-discovery
- Docker image work
- GitHub Action packaging
- broad refactors unrelated to the requested task
