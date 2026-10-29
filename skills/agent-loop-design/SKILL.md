---
name: agent-loop-design
description: Audit and design LLM agent architectures using Anthropic's single-loop guidance - decide which subagents to keep, merge, or fold into skills and tools; decide what belongs in skills vs tools vs knowledge bases vs harness code; and plan an eval-driven migration from multi-agent to one main loop. Use whenever the user is designing, reviewing, or refactoring an agent that has (or might get) subagents, orchestrators, routers, intent classifiers, specialist agents, or agent handoffs; asks whether to split or merge agents, or to add a new agent for a team or domain; is choosing between an agent and a skill in a Claude Code plugin; or complains about agent latency, context lost between agents, conflicting prompt instructions, too many tools, or overlapping agents - even if they never say "fold" or "subagent".
---

# Agent Loop Design

Based on Anthropic's article "Building agents: when to fold subagents into your main agent loop."

## The core stance

Start from one main agent loop with progressive disclosure: domain procedures live in **skills**, actions live in **tools**, and both load only when the task needs them. Treat each subagent as something that has to earn its place with evidence.

Why this is the default:

- **Handoffs lose detail.** Every agent boundary forces a summary. When the work is split by problem type, each hop drops fidelity, like a game of telephone. One shared context lets the model connect results across steps.
- **Speed.** One customer measured roughly 2x faster runs after collapsing a multi-agent harness into a single loop.
- **Newer models carry more per loop.** Starting with Opus 4.5, logic that used to live in orchestration code can move into the model. Rigid multi-agent structures can block that gain when a better model ships. Anthropic cut Claude Code's own system prompt by over 80% for more capable models, moving detail into on-demand skills.
- **Org-chart architectures decay.** When every team gets its own agent, you end up with overlapping agents nobody owns, a system prompt stitched from conflicting team instructions (a "Frankenprompt"), and per-team evals that hide end-to-end regressions.

## When a subagent earns its place

Keep or add a subagent only when at least one of these holds, and you can point to evidence:

1. **Context bloat measurably hurts the single loop.** Eval scores drop as context grows, not just "the prompt feels long."
2. **The work is parallel and benefits from fresh, throwaway context.** Independent research branches, components with clean interfaces, or a black-box verifier that should not see the author's reasoning.
3. **The model struggles to choose tools or reconcile conflicting instructions.** Before splitting for this reason, check whether grouping tools by intent or deferring tool loading fixes it (see `references/placement-guide.md`).

When you do split, **split by context, not by problem type**. A good subagent needs little from the rest of the system and returns a compact result. If a subagent needs most of the conversation to do its job, or returns long prose the next agent has to re-interpret, it should be folded back in.

## Auditing an existing agent

1. **Map the architecture.** For each agent or subagent, record: its job, the context it needs, what it returns, how often it is called, and which agents it chains with. Ask the user for anything you cannot infer from code or config.
2. **Give each one a verdict:**
   - **Keep**: meets a condition above. Name the condition and the evidence.
   - **Merge with X**: chains on X's output, touches the same data, or is usually called together with X.
   - **Call as a tool**: not ready to fold yet; wrap it so the main agent stays in the conversation (see the migration playbook).
   - **Fold**: its prompt becomes a skill, its API calls become tools.
3. **Flag anti-patterns** (list below).
4. **Propose a migration order**: evals first, then merges starting with the most-used agents, then one fold at a time.

Present the audit in this shape:

```markdown
## Architecture map
| Agent | Job | Context needed | Returns | Call frequency | Chains with |

## Verdicts
| Agent | Verdict | Why | Destination (skill / tool / KB / harness) |

## Anti-patterns found

## Evals to build before changing anything

## Migration order
```

## Anti-patterns to flag

- Agents that mirror the org chart, one per team or department
- Splits by problem type that chain into each other (billing agent -> shipping agent -> refund agent)
- A system prompt where each team appended its own rules
- Overlapping agents or skills with no owner
- Only per-team evals, with no shared end-to-end eval
- Business rules written as prompt instructions when a tool could enforce them
- One tool per API endpoint, or more than ~30-50 tools loaded at once
- Code that pastes reference material into the prompt on every turn
- Orchestration logic the current model could handle itself

## Target architecture

- One model and one context window running a tool loop. The harness sets turn and cost budgets and write gates.
- Each turn the model emits a batch of tool calls; the harness runs them in parallel and returns raw results to the same model.
- The model writes a plan early and revises it as results arrive.
- Skills carry ordering and domain procedure. Tools carry hard limits: validation, approval gates, preconditions, permissions.
- Plain code is still the right answer for cheap, almost-always-needed loading (e.g. entity resolution) and mechanical work inside tools.

## Reference files

Read these only when the task calls for them:

- `references/placement-guide.md`: deciding where a piece of logic goes (skill, tool, knowledge base, harness code), plus tool sizing and permissions. Read when folding a subagent or designing a new capability.
- `references/migration-and-evals.md`: the staged migration and how to compare folded vs. unfolded versions. Read when planning or running a migration, or building evals for an agent.
- `references/multi-team-ownership.md`: how several teams contribute to one agent without sprawl. Read when more than one team owns parts of the agent.

## Use existing tooling instead of rebuilding it

If the user builds on the Claude API, point them to the migration kit at `github.com/anthropics/single-agent-loop-kit`. It chains the `/claude-api` skills `build-eval`, `prompt-audit`, `hillclimb`, and `cost-optimize` into a guided workflow and includes a mock-system demo. For managing a skill library, `/skill-creator` authors and audits skills, and `/skill-doctor` reports per-skill cost and usage. This skill supplies the judgment calls (what to fold, in what order, where each piece goes); those tools do the mechanical work.

## Keep the method, not the specifics

This guidance is tied to current model capabilities and will age. What lasts is the method: measure, change one thing at a time, and keep what holds up. Fold one subagent, keep it folded unless the folded version scores worse, and repeat.
