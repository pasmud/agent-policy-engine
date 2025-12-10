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

## Install

Requires Python 3.10+.

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
# optional for development
python -m pip install -e ".[dev]"
```

## Quick start

Evaluate the example calls against the example policy:

```bash
PYTHONPATH=src python -m agent_policy_engine check \
  --policy examples/policy.json \
  --input examples/calls.json \
  --format text
```

Example output (shape):

```text
total=4 allowed=2 denied=2
1. ALLOW tool=web.search agent=research-agent rule=allow-read-tools reason=Low-risk read operations are allowed
2. ALLOW tool=ticket.create agent=support-agent rule=allow-support-ticket-create reason=Support agent may create low/medium priority tickets
3. DENY  tool=shell.exec agent=ops-agent rule=deny-shell reason=Shell execution is blocked
4. DENY  tool=secrets.read agent=research-agent rule=deny-prod-secrets reason=Production secrets cannot be read by agents
```

JSON report:

```bash
PYTHONPATH=src python -m agent_policy_engine check \
  --policy examples/policy.json \
  --input examples/calls.json \
  --format json
```

Write an audit log (JSONL):

```bash
PYTHONPATH=src python -m agent_policy_engine check \
  --policy examples/policy.json \
  --input examples/calls.json \
  --audit-out audit.jsonl
```

Fail the process when any call is denied (useful in CI/policy gates):

```bash
PYTHONPATH=src python -m agent_policy_engine check \
  --policy examples/policy.json \
  --input examples/calls.json \
  --fail-on-deny
# exit code 2 when denied calls exist
```

## Policy format

Policies are JSON documents (YAML is supported only when `PyYAML` is installed). A policy has a default effect and an ordered list of rules.

```json
{
  "version": "1",
  "default_effect": "deny",
  "metadata": {"owner": "security"},
  "rules": [
    {
      "name": "allow-read-tools",
      "effect": "allow",
      "tools": ["filesystem.read", "web.search"],
      "agents": ["*"],
      "actions": ["call"],
      "reason": "Read operations are allowed"
    },
    {
      "name": "deny-prod-secrets",
      "effect": "deny",
      "tools": ["secrets.read"],
      "when": {
        "context.environment": {"eq": "prod"}
      },
      "priority": 90,
      "reason": "No production secrets"
    }
  ]
}
```

### Rule fields

| Field | Type | Default | Description |
|---|---|---:|---|
| `name` | string | required | Unique human-readable rule identifier. |
| `effect` | `"allow" \| "deny"` | required | Decision when rule matches. |
| `tools` | string or list | `["*"]` | `fnmatch` patterns matched against `call.tool`. |
| `agents` | string or list | `["*"]` | Patterns matched against `call.agent`. |
| `actions` | string or list | `["*"]` | Patterns matched against `call.action`. |
| `when` | object | `{}` | Field conditions on call attributes/args/context. |
| `priority` | int | `0` | Higher wins among matched rules. |
| `reason` | string | `""` | Explanation included in decision/report. |

### `when` operators

Conditions are keyed by a path such as `arguments.priority`, `context.environment`, `tool`, `agent`, or `action`.

Supported operators:

- `eq`, `neq`
- `in`, `not_in`
- `contains`, `startswith`, `endswith`, `regex`
- `gt`, `gte`, `lt`, `lte`
- `exists` (boolean)

A scalar value (e.g. `"arguments.env": "prod"`) is treated as `eq`.

## Tool call format

Input can be a single object, a list, or `{"calls": [...]}`.

```json
{
  "call_id": "c1",
  "agent": "support-agent",
  "tool": "ticket.create",
  "action": "call",
  "arguments": {"priority": "medium"},
  "context": {"environment": "dev"}
}
```

## CLI reference

```bash
python -m agent_policy_engine --help
python -m agent_policy_engine check --help
```

`check` command:

- `--policy PATH` (required): policy JSON file.
- `--input PATH` (required): tool call JSON file.
- `--format {json,text}`: report format (default `json`).
- `--audit-out PATH`: write JSONL audit records.
- `--fail-on-deny`: exit with code `2` when any decision is denied.

Exit codes: `0` success, `1` input/validation/runtime error, `2` denied calls with `--fail-on-deny`.

## Python API

