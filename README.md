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

## Install / Download

OpenJarvis is available as a desktop application with automatic model downloading, or via the source code you just pushed to GitHub.

| Platform | Install |
|---|---|
| **Windows** | `irm https://open-jarvis.github.io/OpenJarvis/install.ps1 \| iex` (PowerShell) or use the `.exe` from the [latest release](https://github.com/open-jarvis/OpenJarvis/releases) |
| **macOS / Linux / WSL2** | `curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh \| bash` |
| **From source** | `git clone https://github.com/itsupportgoc-alt/jarvis.git && cd jarvis/OpenJarvis && uv sync --extra desktop --group desktop-native --python 3.12` |

On native Windows the installer needs the MSVC linker (`link.exe`) to compile the Rust extension. If it stops with `MSVC build tools not found`, run this first:

```powershell
winget install --id Microsoft.VisualStudio.2022.BuildTools --override "--wait --quiet --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
```

After install, start the daemon with `jarvis start` and the GUI with `jarvis gui`.

The config fix (`agent = "simple"` in `[server]` section of `~/.openjarvis/config.toml`) is already included in this repository.