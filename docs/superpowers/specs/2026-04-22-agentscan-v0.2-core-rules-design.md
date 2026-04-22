# AgentScan v0.2 Core Rules Design

**Date:** 2026-04-22
**Source:** `AgentScan_SRS_v1.0.md`
**Status:** Draft for review

## Goal

Deliver Milestone **v0.2 — Core Rules** with precision-first static detection by completing the full 17-rule set, adding JSON/SARIF outputs, and shipping a basic but reliable regression-oriented test suite.

## Scope

### Included in v0.2

- Expand builtin static rules from 5 to 17 under existing rule categories:
  - Prompt Injection: `AS-INJ-001` .. `AS-INJ-005`
  - Tool Abuse: `AS-TOOL-001` .. `AS-TOOL-004`
  - Data Leakage: `AS-LEAK-001` .. `AS-LEAK-003`
  - Workflow: `AS-WF-001` .. `AS-WF-005`
- Preserve declarative rule definitions in YAML.
- Add machine-readable report output:
  - JSON
  - SARIF
- Keep deterministic behavior across scan + report outputs.
- Add basic test suite coverage for rule behavior, formatter outputs, and CLI integration.
- Allow **light pattern/wording refinements** to reduce false positives in existing fixtures.
- Update docs (`AgentScan_SRS_v1.0.md`, `README.md`, and `AGENTS.md` if needed) when behavior expectations change.

### Explicitly excluded from v0.2

- Embedding/semantic similarity detection (v0.3+)
- LLM judge integration (v1.0+)
- Provider-aware auto-discovery expansion
- Docker/GitHub Action packaging
- Broad refactor unrelated to static rules and output formats

## Precision-First Rule Policy

v0.2 prioritizes precision over recall:

- Prefer contextual patterns over broad keyword-only regexes.
- Restrict high-severity findings to stronger signal patterns where possible.
- Require tests for both positive and near-miss negative cases for each rule family.
- Any intentional behavior shift to reduce false positives must be reflected in docs and tests.

## Architecture

Pipeline remains:

`discover -> parse -> normalize -> evaluate rules -> aggregate findings -> format output -> exit code`

### Design constraints

- One canonical finding model feeds all output formats.
- Formatter layer (console/json/sarif) must not alter detection semantics.
- Stable ordering is enforced before final render/serialization.
- Existing CLI defaults remain backward compatible (console output by default).

## Component Changes

### Rules (`src/agentscan/builtin_rules/*.yml`)

- Add missing 12 rules to reach 17 total.
- Refine matching patterns and conditions for lower false-positive rate.
- Preserve stable rule IDs and severity intent from SRS.

### Rule execution (`src/agentscan/rules.py`, `src/agentscan/scanner.py`)

- Ensure rule loading/execution supports expanded set without scanner-flow changes.
- Keep deterministic finding ordering.

### Reporting (`src/agentscan/reporting.py` and CLI integration)

- Add JSON formatter implementation.
- Add SARIF formatter implementation.
- Keep console formatter unchanged unless required for shared model alignment.

### CLI (`src/agentscan/cli.py`)

- Add output-format selection (console/json/sarif).
- Preserve current default behavior and CI-friendly exit code logic.

## Data Flow Details

1. Discovery returns ordered candidate files.
2. Parser emits canonical artifacts, with non-fatal parse warnings where needed.
3. Rules engine evaluates 17 rules against canonical fields/tools.
4. Findings are aggregated and sorted deterministically.
5. Reporter serializes by selected output format:
   - console: human-readable table/lines
   - json: machine-readable structured payload
   - sarif: SARIF run/results/rules mapping
6. CLI applies `fail-on` threshold and returns final exit code.

## Error Handling

- Invalid structured input file: continue scan with parse warnings.
- Unsupported/invalid output format option: fail fast with clear CLI error.
- Serialization failure in JSON/SARIF formatter: return explicit operational error.
- No supported files behavior remains unchanged from v0.1.

## Testing Strategy

### Required test coverage for v0.2

1. Rule tests:
   - Positive detection tests for all 17 rules.
   - Negative/near-miss tests to guard precision.
2. Output tests:
   - JSON structure + deterministic ordering checks.
   - SARIF structural validity and expected field mapping checks.
3. CLI integration tests:
   - `scan` with default console output.
   - `scan --format json`.
   - `scan --format sarif`.
4. Fixture regression tests:
   - Verify reduced false positives on existing fixtures.
   - Preserve deterministic outputs.

## Documentation Synchronization Plan

When rule wording/pattern behavior changes:

- `AgentScan_SRS_v1.0.md`: clarify rule intent/wording at requirement level if needed.
- `README.md`: update user-visible behavior, CLI examples, and output format docs.
- `AGENTS.md`: update verification/development guidance only if workflow expectations changed.

## Acceptance Criteria

- 17 static rules are implemented and loaded from builtin YAML.
- JSON and SARIF outputs are available via CLI and covered by tests.
- Existing scan behavior remains deterministic.
- Precision-first regression tests pass on safe/unsafe/empty fixtures.
- Documentation reflects any intentional behavior changes.
