# OpenJarvis Config Fix

## Problem

The OpenJarvis daemon defaults to the `orchestrator` agent, which sends native tool schemas to Ollama while also demanding a `THOUGHT/TOOL/INPUT...FINAL_ANSWER` text protocol in the system prompt. With `llama3.2:3b`, the model splits the difference and outputs raw JSON like `{"name": "calculator", "parameters": {"code": "17*23"}}` instead of structured tool calls.

## Fix

Set `agent = "simple"` in the `[server]` section of `~/.openjarvis/config.toml`.

```toml
[server]
agent = "simple"
```

## Verified

- GUI chat now returns prose instead of raw tool JSON
- Your three example prompts now answer normally
- Server PID reports `Agent: simple` on startup