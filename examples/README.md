# Examples

This directory contains a minimal policy and a batch of tool calls.

## Run the demo

From the repository root:

```bash
PYTHONPATH=src python -m agent_policy_engine check \
  --policy examples/policy.json \
  --input examples/calls.json \
  --format text
```

## Expected behavior

- `web.search` is allowed by `allow-read-tools`.
- `ticket.create` for a support agent with medium priority is allowed.
- `shell.exec` is denied by the high-priority `deny-shell` rule.
- `secrets.read` in `prod` context is denied by `deny-prod-secrets`.

The JSON report format (`--format json`) includes a summary and per-call decision details, including matched rule names and reasons.
