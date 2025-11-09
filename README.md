# agent-policy-engine

`agent-policy-engine` is a small, deterministic policy engine for evaluating agent tool calls. It applies allow/deny rules, returns explainable decisions, and records an audit trail. The project is designed for offline, testable policy checks in agent runtimes, CI gates, or local simulations.

## Features

- **Rule-based allow/deny decisions** with explicit default effect.
- **Pattern matching** for tools, agents, and actions (`fnmatch` wildcards like `shell.*`).
- **Conditional matching** on `arguments.*` and `context.*` fields (`eq`, `neq`, `in`, `contains`, `regex`, numeric comparisons, `exists`).
- **Priority-aware evaluation**: matching rules are resolved by highest `priority`; ties preserve policy order.
- **Audit logging**: decisions can be recorded in memory and exported as JSONL.
- **CLI and Python API**: evaluate single/batch calls from JSON files.
- **Deterministic, offline tests**: stdlib-first implementation; optional PyYAML only if you load YAML policies.

