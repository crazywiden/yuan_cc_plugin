# Multiple teams, one agent

In large organizations the instinct is one agent per team. That produces the failure modes this skill exists to prevent: overlapping agents nobody owns, a system prompt with conflicting rules from every team, details lost at handoffs, and per-team evals that each look fine while the end-to-end experience gets worse. The alternative is one loop with clear ownership of its parts.

## Who owns what

| Owner | Owns |
|---|---|
| **Small central team** | The system prompt, end-to-end quality, the shared eval set, and vetting every new tool, skill, and eval before it ships |
| **Domain teams** | Their own skills and tools, each with a named directly responsible individual (DRI), plus their per-skill evals |

A domain team that needs new behavior adds a skill or a tool, not a new agent and not new lines in the system prompt.

## Preventing skill sprawl

Skills can sprawl the same way agents do. Guard against it with:

- **Ownership**: every skill has a DRI. A skill without one is a candidate for removal.
- **Distinctness checks**: before adding a skill, check that no existing skill already covers it. Overlapping skills confuse selection the same way overlapping agents confuse routing.
- **Evals**: a skill without an eval cannot be safely changed or removed.
- **Pruning**: use `/skill-creator` to author and audit skills, and `/skill-doctor` to measure per-skill cost and usage. Remove skills that are never used.

## Tools across teams

Tool count is a shared budget. Tool choice degrades past roughly 30-50 definitions, so the central team should push back on one-tool-per-endpoint designs and keep tool search with deferred loading in place as the catalog grows.
