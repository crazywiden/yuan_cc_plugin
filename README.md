# Yuan's Claude Code Plugin

A collection of custom Claude Code skills, agents, and commands for ads API development, brainstorming, competitive research, and productivity workflows.

## Features

### Skills
- **google-ads-api-skill** - Implement and debug Google Ads API integrations
- **tiktok-ads-api-skill** - Implement and debug TikTok Ads API integrations
- **brainstorming** - Creative ideation and feature exploration
- **competitive-ads-extractor** - Extract and analyze competitors' ads
- **competitor-market-research** - Analyze competitors and market landscape
- **lead-research-assistant** - Identify high-quality leads
- **startup-deep-dive** - Deep analysis of startup companies
- **writing-skills** - Create and edit Claude Code skills
- **agent-loop-design** - Decide when to fold subagents into one main agent loop

### Agents
- **backend-planner** - Principal Backend Architect for repo-aligned designs
- **frontend-planner** - Principal Frontend Architect for UI/UX specs
- **devops-engineer** - Expert DevOps for automation and infrastructure
- **debugger** - Systematic bug analysis through evidence gathering
- **google-ads-debugger** - Specialized Google Ads debugging
- **google-ads-dev** - Google Ads API development specialist

### Commands
- **think-hard** - Double-check work and generated output
- **backend-task-design** - Design backend tasks using ultrathink mode
- **frontend-task-design** - Design frontend tasks using ultrathink mode
- **git-helper** - Expert Git assistance for commits and operations
- **discuss** - Thorough technical discussions
- **create-worktree** - Automate git worktree creation

## Prerequisites

### Required MCP Servers

Some agents depend on external MCP servers. Install these if you plan to use the agents that require them.

**Context7** (used by: `backend-planner`, `frontend-planner`, `devops-engineer`, `google-ads-debugger`)

Context7 provides up-to-date documentation lookup for third-party APIs. Add it to your MCP configuration (`.mcp.json` or via Claude Code settings):

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

**Playwright** (used by: `frontend-planner`)

Playwright provides browser automation for UI inspection. Add it to your MCP configuration:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-playwright"]
    }
  }
}
```

### Agents that work without MCP setup

These agents and all skills/commands work out of the box with no additional configuration:
- **debugger**
- **google-ads-dev**

## Installation

### Option 1: Add as marketplace and install (Recommended)

1. Add the marketplace:
```bash
/plugin marketplace add crazywiden/yuan_cc_plugin
```

2. Install the plugin:
```bash
/plugin install yuan-cc-plugin@yuan_cc_plugin
```

### Option 2: Local development/testing

```bash
claude --plugin-dir /path/to/yuan_cc_plugin
```

## Usage

After installation, skills will be available with the plugin namespace prefix:

```
/yuan-cc-plugin:brainstorming
/yuan-cc-plugin:google-ads-api-skill
/yuan-cc-plugin:competitor-market-research
```

Commands are available as:
```
/yuan-cc-plugin:think-hard
/yuan-cc-plugin:git-helper
```

## Optional: Example Settings

The `settings.example.json` file contains example permissions and hooks configuration. You can copy relevant parts to your own Claude Code settings:

- `~/.claude/settings.json` - User-level settings
- `.claude/settings.json` - Project-level settings
- `.claude/settings.local.json` - Local project settings (gitignored)

**Note:** The example hooks use `afplay` which is macOS-only. The `statusLine` references `~/.claude/time_check.sh` which is not included in this plugin — you'll need to provide your own script or remove that section.

## License

MIT
