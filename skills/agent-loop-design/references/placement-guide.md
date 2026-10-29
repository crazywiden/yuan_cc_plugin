# Placement guide: skill, tool, knowledge base, or harness code

When you fold a subagent, or design a new capability, each piece of logic needs a home. Put it where it is cheapest to load and hardest to get wrong.

## The four destinations

| Destination | What goes here | Why here |
|---|---|---|
| **Skill** | How a team does its work: steps, ordering, conventions, judgment calls | Loaded only when relevant, so the system prompt stays small. The owning team can edit it without touching the core prompt. |
| **Tool** | Actions, live data, fixed-shape results, validation, approval gates, hard preconditions, per-user permission checks | The model cannot skip a check that lives inside the tool. A prompt instruction can be ignored; a tool refusal cannot. |
| **Knowledge base** | Reference material needed only sometimes: policies, catalogs, specs | Served through a search or lookup tool, or as a reference file inside a skill. It costs nothing until it is needed. |
| **Harness code** | Cheap, almost-always-needed loading (e.g. entity resolution), mechanical work like building payloads, turn and cost budgets, write gates | Deterministic work does not need the model, and things needed on every turn are not worth a tool call. |

The system prompt itself should stay small: identity, the core stance, and whatever every single turn truly needs.

## Quick test

| If the instruction sounds like... | Put it in |
|---|---|
| "Our team usually does A, then B, unless C" | Skill |
| "Never issue a refund over $500 without approval" | Tool (approval gate) |
| "Only admins can change billing settings" | Tool (permission check that returns a readable refusal) |
| "Here is the 40-page returns policy" | Knowledge base or skill reference file |
| "Look up the customer record at the start of every request" | Harness code |
| "Format the API payload like this" | Harness code inside the tool |

## Tool design

- **Group tools by user intent, not one per API endpoint.** `update_order(order_id, changes)` beats `set_shipping_address`, `set_quantity`, and `set_gift_note` as three separate tools.
- **Watch the count.** Tool choice tends to degrade past roughly 30-50 tool definitions. Beyond that, use tool search with deferred loading so only relevant definitions enter context.
- **Put hard preconditions inside the tool**, and have the tool return readable instructions when a precondition fails ("Verify the customer's identity with `verify_identity` before calling this"). The model can recover from a clear message; it cannot recover from a stack trace.
- **Enforce per-user permissions in the tool** with a plain refusal. One loop can then serve users with different access levels, instead of a separate agent per role.

## Knowledge bases

Reach for a lookup tool or a reference file inside a skill when material is needed only some of the time. Avoid code that pastes context into the prompt on every turn: it pays the token cost on every turn and crowds out the context the task actually needs.
