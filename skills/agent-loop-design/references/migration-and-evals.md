# Migration and eval playbook

Moving from multi-agent to a single loop is a series of small, measured changes. Changing several things at once makes it impossible to tell which change caused a regression.

## Stage 1: Build evals first

Nothing else is safe until you can measure end-to-end quality.

- **Shared end-to-end set**, owned by a central team. Ten golden examples is enough to start.
- **Small per-skill sets**, owned by the domain teams.
- **Grade final answers against a rubric**, not intermediate steps.
- **Track routing accuracy** while an orchestrator still exists. Once folded, track whether the right skill or tool was used instead.
- **Timestamp key events** in production runs so real traffic can be replayed as targeted evals.

Coverage matters more than size. Make sure the set has:

- a task for every chain of agents that runs together in production, because folding is most likely to break the handoffs between them
- a task for every rule the agent must not break, because a faster, cheaper version that breaks one invariant is a regression

## Stage 2: Merge tightly coupled specialists

Merge specialists that:

- chain on each other's output
- touch the same data
- are usually called together

Start with the most-used ones; that is where the latency and handoff losses add up fastest.

## Stage 3: Call the remaining subagents as tools

Instead of handing the conversation to a subagent, call it like a tool:

- The main agent stays in the conversation.
- All subagents return a shared response schema.
- The main agent verifies subagent conclusions against real data rather than trusting them.
- Trim what goes into the final synthesis to what it actually needs.
- Use a full handoff only when the subagent must talk to the user directly.

This stage also gives you the **baseline** for the next one.

## Stage 4: Fold in one subagent at a time

For each subagent:

1. Turn its prompt into a skill and its API calls into tools (MCP tools if you use MCP).
2. Run the eval with and without the fold.
3. Keep the subagent only if the folded version scores worse.

When comparing:

- **Look at which tasks flipped, not just the aggregate score.** In the article's support-agent example, folding a shipping specialist lowered latency but broke the delivery-date process. The aggregate could hide that.
- **Run each task several times.** That same regression showed up in only one of two runs. Single runs miss intermittent breaks.

## Tooling (Claude API)

The migration kit at `github.com/anthropics/single-agent-loop-kit` chains these `/claude-api` skills and includes a mock-system demo:

| Skill | Use |
|---|---|
| `build-eval` | Build the end-to-end or per-skill eval set |
| `prompt-audit` | Flag instructions written for older models and propose diffs |
| `hillclimb` | Iteratively improve the app against the eval, including folded vs. kept comparisons |
| `cost-optimize` | Profile calls and propose savings (caching, trimming tokens, effort, model choice), one change at a time |
