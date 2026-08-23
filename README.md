# Roblox Studio Antigravity Plugin

A self-contained Antigravity plugin providing robust integration with Roblox Studio via the Roblox Studio MCP server.

---

## Plugin Package Structure

```
roblox-studio/
├── plugin.json                 # Plugin manifest
├── mcp_config.json             # MCP server configuration (direct Python wrapper)
├── studiomcp_wrapper.py        # Wrapper that locates StudioMCP.exe dynamically
├── README.md                   # Plugin overview and documentation
├── rules/
│   └── AGENTS.md               # Active rules and guardrails for Studio operations
└── skills/
    └── roblox-studio-mcp/
        ├── SKILL.md            # Primary operational guide and workflows
        └── references/
            ├── luau-execution-guide.md  # Safe Luau coding patterns & engine limits
            ├── tool-reference.md        # Reference for all 28 Roblox MCP tools
            └── troubleshooting.md       # Error recovery and symptom runbook
```

---

## Features

1. **Resilient Connection Architecture**:
   - Executes `python studiomcp_wrapper.py` directly to avoid batch syntax issues and withstand Roblox Studio automatic updates.
   - Intercepts early `server/discover` probes to prevent StudioMCP crash-on-startup.
2. **Safe Luau Execution**:
   - Prevents engine lockups and thread blocking with explicit yield requirements.
   - Enforces serializable return objects to avoid JSON-RPC transport drops.
3. **DataModel & State Awareness**:
   - Enforces mode-safe execution (`Edit` vs `Client`/`Server` playtesting).
4. **Engine Limit Safeguards**:
   - Handles the 200,000-character `Script.Source` engine constraint with modularization strategies.

---

## How to Install / Distribute

### In a Project Workspace:
Place the `roblox-studio` (this whole folder) folder into your project's `.agents/plugins/` directory:
```
<project_root>/.agents/plugins/roblox-studio/
```

### Globally across Machine:
Place the plugin directory into your Antigravity global plugins folder:
```
~/.gemini/antigravity/plugins/roblox-studio/
```

### Local Configuration Note:
`mcp_config.json` calls the bundled `studiomcp_wrapper.py`. The wrapper discovers `StudioMCP.exe` automatically from the registry or `%LOCALAPPDATA%`, so no user-specific path should be required.
