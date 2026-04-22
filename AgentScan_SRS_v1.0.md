# AgentScan — AI Agent Security Scanner
## Software Requirements Specification (SRS)
**Version 1.0 — Draft | April 2026**

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | April 2026 | TBD | Initial draft |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [System Architecture](#5-system-architecture)
6. [Detection Rules v1.0](#6-detection-rules-v10)
7. [Out of Scope](#7-out-of-scope-v10)
8. [Development Milestones](#8-development-milestones)
9. [Open Questions](#9-open-questions)

---

## 1. Introduction

### 1.1 Purpose

This document specifies the software requirements for **AgentScan** — an open-source static security scanner designed to detect vulnerabilities in AI agent skill definitions, workflow configurations, and prompt templates. AgentScan enables developers and security teams to identify security issues before deployment to production environments.

### 1.2 Scope

AgentScan provides static analysis of AI agent artifacts, covering four vulnerability categories:

- **Prompt injection** vulnerabilities embedded in system prompts and skill definitions
- **Tool/function call abuse** via dangerous tool combinations or unrestricted parameters
- **Data leakage risks** in workflow output handling
- **Insecure agent workflow patterns** including missing input/output validation

AgentScan targets AI developer teams, DevSecOps engineers, and security researchers building or auditing AI agent systems.

### 1.3 Definitions and Acronyms

| Term | Definition |
|------|------------|
| AI Agent | An autonomous software system powered by an LLM that can execute tools and complete multi-step tasks |
| Skill | A reusable capability definition for an AI agent, typically expressed as YAML or JSON containing system prompts and tool bindings |
| Workflow | A directed sequence of agent actions, tool calls, and decision logic (e.g., LangGraph, CrewAI pipelines) |
| MCP | Model Context Protocol — a standard for connecting AI agents to external tools and data sources |
| Prompt Injection | An attack where malicious content in inputs manipulates an LLM to deviate from its intended behavior |
| Tool Poisoning | Manipulation of tool definitions to cause an agent to misuse or abuse tool capabilities |
| SRS | Software Requirements Specification |
| OWASP LLM Top 10 | The Open Web Application Security Project's top 10 vulnerabilities for LLM applications (2025 edition) |

### 1.4 References

- OWASP Top 10 for LLM Applications 2025
- OWASP Top 10 for Agentic AI Applications 2026
- MITRE ATLAS — Adversarial Threat Landscape for AI Systems
- [AgentAuditKit](https://github.com/sattyamjjain/agent-audit-kit) — related open-source tool
- [Garak](https://github.com/NVIDIA/garak) — NVIDIA LLM vulnerability scanner
- [Microsoft PyRIT](https://github.com/Azure/PyRIT) — Python Risk Identification Toolkit

---

## 2. Overall Description

### 2.1 Product Perspective

AgentScan occupies a distinct niche in the AI security tooling landscape. Unlike existing tools that focus on dynamic testing (sending adversarial inputs to a live LLM), AgentScan performs **static analysis** of AI agent artifacts — the source files that define agent behavior before deployment.

AgentScan complements existing tools rather than replacing them:

| Tool | Approach | Focus | AgentScan Relationship |
|------|----------|-------|------------------------|
| Garak | Dynamic | LLM model behavior | Complementary — runtime testing vs. static artifacts |
| PyRIT | Dynamic | Multi-turn red teaming | Complementary — deep exploit vs. preventive scan |
| AgentAuditKit | Static | MCP config files & secrets | Complementary — infra layer vs. semantic layer |
| **AgentScan** | **Static** | **Skill/workflow semantics & prompts** | **This tool** |

### 2.2 Product Functions

1. Static analysis of skill definition files (YAML, JSON) for embedded prompt injection patterns
2. Detection of dangerous tool combination patterns that could lead to data exfiltration
3. Workflow logic analysis for missing validation, unsanitized outputs, and insecure data flows
4. Semantic analysis using LLM-based judgment for complex, context-dependent vulnerabilities
5. Severity scoring and remediation guidance for each finding
6. CI/CD integration via exit codes and structured report output (JSON, SARIF)
7. Optionally deployable as an Agent Skill for runtime self-scan within agent pipelines

### 2.3 User Classes

| User Class | Description | Primary Use Case |
|------------|-------------|-----------------|
| AI Developer | Engineers building AI agent applications and workflows | Pre-commit scan, local development |
| DevSecOps Engineer | Security engineers integrating scans into CI/CD pipelines | Automated PR scanning, compliance reporting |
| Security Researcher | Researchers auditing third-party AI agent skills and plugins | Bulk scan of published skill libraries |
| Platform Engineer | Teams operating AI agent infrastructure | Runtime integration as an Agent Skill |

### 2.4 Constraints

- AgentScan performs static analysis only — it does not execute code or send requests to LLM APIs by default
- LLM-based semantic analysis (optional) requires API key configuration and incurs cost
- False positive rate is expected to be higher for semantic rules vs. pattern-based rules
- The tool does not replace dynamic testing or manual security review

### 2.5 Assumptions and Dependencies

- Input files are readable text-based formats (YAML, JSON, TOML, Markdown)
- Python 3.10+ runtime available in target environments
- Optional LLM judge requires network access to Anthropic or OpenAI API

---

## 3. Functional Requirements

### 3.1 Input Handling

**FR-INPUT-001: Multi-format Support**
The system SHALL accept the following input formats:
- YAML skill definition files (`.yaml`, `.yml`)
- JSON agent configuration files (`.json`)
- LangChain agent configs and chain definitions
- CrewAI agent and task YAML definitions
- Claude skill/tool definition formats
- AutoGen agent configuration files
- Plain text prompt files (`.txt`, `.md`)

**FR-INPUT-002: Directory Scanning**
The system SHALL recursively scan a directory and discover all recognized agent artifact files, with configurable include/exclude patterns.

**FR-INPUT-003: Input Normalization**
The system SHALL normalize all input text prior to analysis, including:
- Unicode normalization (NFKC)
- Removal of zero-width characters
- Decoding of common encoding schemes (base64, URL encoding) found within text fields

### 3.2 Prompt Injection Detection

**FR-INJECT-001: Pattern-Based Detection**
The system SHALL detect prompt injection patterns including:
- Instruction override phrases (e.g., "ignore previous instructions", "disregard your guidelines")
- Role reassignment attempts (e.g., "you are now", "act as", "pretend you are")
- Hidden instructions using Unicode obfuscation or invisible characters
- Encoded injection payloads (base64, hex, ROT13 within prompt fields)
- Multi-language injection patterns including Vietnamese, Chinese, Arabic, and other non-Latin scripts

**FR-INJECT-002: Semantic Injection Detection**
The system SHOULD optionally use an LLM-based judge to detect semantically obfuscated injection attempts that evade pattern matching. The LLM judge SHALL operate in a sandboxed context isolated from the content being analyzed.

**FR-INJECT-003: Context-Aware Analysis**
The system SHALL differentiate severity based on injection location:
- System prompts → HIGH severity
- User-facing instructions → MEDIUM severity
- Example/sample content → LOW severity

### 3.3 Tool/Function Call Abuse Detection

**FR-TOOL-001: Dangerous Tool Combination Detection**
The system SHALL flag dangerous tool combinations that create data exfiltration or lateral movement risks:

| Combination Pattern | Risk | Severity |
|---------------------|------|----------|
| `filesystem_read` + `http_post` / `send_email` | Data exfiltration via file read + outbound call | CRITICAL |
| `shell_exec` / `code_execute` (unrestricted) | Arbitrary code execution | CRITICAL |
| `database_query` + `external_api` (no scope) | Database content leakage | HIGH |
| `read_calendar` + `send_message` | PII exfiltration via calendar access | HIGH |
| `web_search` + `file_write` | Remote content injection to local files | MEDIUM |

**FR-TOOL-002: Unrestricted Parameter Detection**
The system SHALL flag tool definitions lacking parameter constraints, such as shell execution tools with no command whitelist or file system tools with no path restrictions.

**FR-TOOL-003: Tool Definition Integrity**
The system SHALL detect anomalies in tool descriptions that may indicate tool poisoning, including invisible Unicode characters, unusually long descriptions, and embedded instructions targeting the LLM.

### 3.4 Data Leakage Detection

**FR-LEAK-001: Output Handling Analysis**
The system SHALL detect workflow configurations that pass raw LLM outputs to external systems without sanitization or filtering.

**FR-LEAK-002: PII Exposure Patterns**
The system SHALL detect prompts and workflow steps that request or handle PII (names, emails, addresses, credentials) without explicit data handling policies.

**FR-LEAK-003: Secret Detection**
The system SHALL detect hardcoded credentials, API keys, and tokens within skill and workflow files using entropy analysis and pattern matching.

### 3.5 Insecure Workflow Detection

**FR-WORKFLOW-001: Missing Validation**
The system SHALL flag workflow definitions that lack input validation before passing data to tools, or lack output sanitization before returning results to users.

**FR-WORKFLOW-002: Excessive Agency**
The system SHALL detect configurations granting agents excessive autonomy:
- Auto-approval of all tool calls
- Absence of human-in-the-loop checkpoints for high-risk actions
- Unbounded iteration limits

**FR-WORKFLOW-003: Insecure Memory Patterns**
The system SHALL detect patterns where agent memory stores are written without access controls or read back into prompts without sanitization, creating memory poisoning risks.

### 3.6 Reporting

**FR-REPORT-001: Finding Structure**
Each finding SHALL include:
- Rule ID
- Severity level (CRITICAL / HIGH / MEDIUM / LOW / INFO)
- Affected file and line number
- Evidence snippet
- Human-readable description
- Recommended remediation

**FR-REPORT-002: Output Formats**
The system SHALL support output in: console (human-readable), JSON (machine-readable), and SARIF (for GitHub/GitLab security tab integration).

**FR-REPORT-003: OWASP Mapping**
Each finding SHALL be mapped to the relevant OWASP LLM Top 10 (2025) and/or OWASP Agentic AI Top 10 (2026) identifier.

---

## 4. Non-Functional Requirements

### 4.1 Performance

- **NFR-PERF-001:** Static analysis of a single skill file SHALL complete in under 500ms
- **NFR-PERF-002:** Full directory scan of 100 skill files SHALL complete in under 30 seconds without LLM analysis
- **NFR-PERF-003:** LLM-based semantic analysis is exempt from performance requirements due to external API latency

### 4.2 Security

- **NFR-SEC-001:** The tool itself SHALL NOT send any scanned content to external services without explicit user opt-in
- **NFR-SEC-002:** LLM judge prompts SHALL be hardcoded and isolated — the content being scanned SHALL NOT be able to modify judge behavior
- **NFR-SEC-003:** The tool SHALL run with read-only filesystem access to scanned directories
- **NFR-SEC-004:** All dependencies SHALL be pinned to specific versions with hash verification

### 4.3 Reliability

- **NFR-REL-001:** The tool SHALL exit with a non-zero code if CRITICAL or HIGH findings are detected (configurable threshold)
- **NFR-REL-002:** Malformed input files SHALL produce a warning, not a crash — the tool SHALL continue scanning remaining files
- **NFR-REL-003:** Test coverage SHALL be maintained at a minimum of 80% for all detection rules

### 4.4 Usability

- **NFR-USE-001:** A user with no prior configuration SHALL be able to run their first scan with a single command: `agentscan scan .`
- **NFR-USE-002:** All findings SHALL include actionable remediation guidance, not just vulnerability descriptions
- **NFR-USE-003:** False positive suppression SHALL be configurable via inline comments or a `.agentscan.yml` config file

### 4.5 Maintainability

- **NFR-MAINT-001:** Detection rules SHALL be defined in a declarative YAML format separate from engine code, enabling community contributions without Python knowledge
- **NFR-MAINT-002:** Adding a new rule SHALL not require modification of core scanner logic
- **NFR-MAINT-003:** The project SHALL maintain a public CHANGELOG and follow semantic versioning

### 4.6 Portability

- **NFR-PORT-001:** The tool SHALL support Python 3.10+ on Linux, macOS, and Windows
- **NFR-PORT-002:** Core functionality SHALL operate fully offline with zero cloud dependencies
- **NFR-PORT-003:** A Docker image SHALL be provided for CI/CD environments

---

## 5. System Architecture

### 5.1 High-Level Pipeline

```
Input (skill files / workflow configs / prompt templates)
         │
         ▼
┌─────────────────┐
│   Preprocessor  │  Discover files, parse YAML/JSON, normalize Unicode,
│                 │  decode obfuscated content, chunk long inputs
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Static Analyzer │  Pattern-based rules engine — regex, AST analysis,
│                 │  entropy detection. Fast, no LLM required.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Semantic Analyzer│  Embedding similarity vs. known attack pattern DB.
│   (optional)    │  Local model, no API key required.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM Judge     │  Sandboxed LLM for complex, context-dependent findings.
│   (optional)    │  Requires API key. Receives sanitized representation only.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Reporter     │  Aggregate findings, severity scoring,
│                 │  output: console / JSON / SARIF
└─────────────────┘
```

### 5.2 Anti-Bypass Mechanisms

This is a core design challenge — preventing attackers from crafting skill files that evade detection.

#### 5.2.1 Multi-Layer Detection
Each vulnerability class is covered by at least two independent detection methods. An attack must evade ALL layers simultaneously to avoid detection.

#### 5.2.2 Sliding Window Analysis
Long-context injection attacks that embed malicious content deep in large files are detected via sliding window chunking — no single chunk is trusted as benign based on length alone.

#### 5.2.3 Unicode & Encoding Normalization
All text is normalized before analysis:
- NFKC Unicode normalization
- Zero-width character stripping
- Homoglyph detection (e.g., Cyrillic `а` vs Latin `a`)
- Decoding of base64/URL/hex encoded strings within text fields

An attacker cannot use `Ign\u200Bore` to bypass the `Ignore` detector.

#### 5.2.4 LLM Judge Isolation
The LLM judge receives a **sanitized structural representation** of the artifact, not raw content. The judge's system prompt is hardcoded at compile time. Even if the scanned file contains "ignore your analysis instructions", this content is presented as *data* to the judge, not as instructions.

```
# What the LLM judge receives (NOT the raw file):
{
  "artifact_type": "skill_definition",
  "system_prompt_tokens": 142,
  "tool_names": ["filesystem_read", "send_email"],
  "suspicious_patterns_flagged_by_static": ["instruction_override_keyword"],
  "structural_anomalies": ["zero_width_chars_detected"]
}
```

#### 5.2.5 Rule Versioning & Pinning
Detection rules are versioned and hash-pinned. A CI/CD pipeline can verify that rules have not been tampered with between scans.

### 5.3 Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Core Engine | Python 3.10+ | Best ecosystem for AI/security tooling |
| CLI Interface | Click | Industry standard Python CLI framework |
| YAML/JSON Parsing | PyYAML + orjson | Robust parsing with error recovery |
| Pattern Rules | Declarative YAML rules | Community-contributable without Python knowledge |
| Semantic Embeddings | sentence-transformers | Local model, no API key required |
| LLM Judge (optional) | Anthropic / OpenAI API | Configurable provider, sandboxed context |
| SARIF Output | sarif-om | Standard security scan result format |
| CI/CD | GitHub Actions + Docker | Broad adoption in target user base |

---

## 6. Detection Rules (v1.0)

| Rule ID | Category | Description | Severity | OWASP |
|---------|----------|-------------|----------|-------|
| AS-INJ-001 | Prompt Injection | Instruction override keywords in system prompt | HIGH | LLM01 |
| AS-INJ-002 | Prompt Injection | Role reassignment in prompt fields | HIGH | LLM01 |
| AS-INJ-003 | Prompt Injection | Zero-width Unicode in prompt content | CRITICAL | LLM01 |
| AS-INJ-004 | Prompt Injection | Base64/encoded content in prompt fields | MEDIUM | LLM01 |
| AS-INJ-005 | Prompt Injection | Multi-language injection patterns (non-Latin) | HIGH | LLM01 |
| AS-TOOL-001 | Tool Abuse | `filesystem_read` + outbound tool combination | CRITICAL | LLM06 |
| AS-TOOL-002 | Tool Abuse | Unrestricted shell/code execution tool | CRITICAL | LLM06 |
| AS-TOOL-003 | Tool Abuse | Tool description contains LLM-targeting instructions | HIGH | LLM06 |
| AS-TOOL-004 | Tool Abuse | Missing parameter constraints on sensitive tools | MEDIUM | LLM06 |
| AS-LEAK-001 | Data Leakage | PII handling without data policy annotation | MEDIUM | LLM02 |
| AS-LEAK-002 | Data Leakage | Raw LLM output passed to external system unfiltered | HIGH | LLM02 |
| AS-LEAK-003 | Data Leakage | Hardcoded secret or API key in skill file | CRITICAL | LLM02 |
| AS-WF-001 | Workflow | Missing input validation before tool call | MEDIUM | LLM08 |
| AS-WF-002 | Workflow | Auto-approval of all tool calls (excessive agency) | HIGH | LLM08 |
| AS-WF-003 | Workflow | Unbounded agent iteration / no termination condition | MEDIUM | LLM08 |
| AS-WF-004 | Workflow | Memory read-back without sanitization | HIGH | LLM08 |
| AS-WF-005 | Workflow | Missing human-in-the-loop for high-risk tool calls | MEDIUM | LLM08 |

---

## 7. Out of Scope (v1.0)

The following capabilities are explicitly excluded from v1.0:

- **Dynamic testing** — sending adversarial inputs to live LLM endpoints
- **MCP config file scanning** for secrets/authentication (covered by AgentAuditKit)
- **Supply chain analysis** of npm/pip packages used by MCP servers
- **Compliance report generation** (EU AI Act, SOC2) — planned for v1.2
- **Web-based UI dashboard** — planned for v2.0
- **IDE plugin** (VS Code, JetBrains) — planned for v2.0
- **Automatic remediation** / fix suggestions beyond text guidance

---

## 8. Development Milestones

| Milestone | Target | Deliverables |
|-----------|--------|--------------|
| v0.1 — Prototype | Week 3 | CLI scaffold, YAML parser, 5 pattern-based rules (AS-INJ-001~003, AS-TOOL-001, AS-LEAK-003) |
| v0.2 — Core Rules | Week 6 | Full static rule set (17 rules), JSON/SARIF output, basic test suite |
| v0.3 — Semantic Layer | Week 9 | Embedding-based similarity detection, sliding window analysis, false positive tuning |
| v1.0 — Release | Week 12 | LLM judge (optional), GitHub Action, Docker image, documentation, public GitHub release |
| v1.1 — Community | Week 16 | Community rule contributions framework, rule YAML schema, plugin interface |

---

## 9. Open Questions

| # | Question | Status |
|---|----------|--------|
| 1 | Should the LLM judge use a self-hosted model (e.g., Ollama) as default to avoid API key requirement for first-time users? | Open |
| 2 | What is the acceptable false positive rate threshold for semantic rules before they are considered "stable"? | Open |
| 3 | Should AgentScan integrate with or extend AgentAuditKit rather than being a standalone tool? | Open |
| 4 | Which agent workflow formats should be prioritized: LangChain, CrewAI, AutoGen, or Claude Skills? | Open |
| 5 | How should multi-language (non-English) attack patterns be maintained and updated over time? | Open |

---

*AgentScan — Open Source AI Agent Security Scanner*
*Version 1.0 Draft — April 2026*
