---
description: One sentence describing what this agent does and when to use it — "Use when...".
tools: [view, edit, create, glob, grep, bash]
---

<!--
This is the Copilot custom-agent format: agents/<your-plugin-name>.agent.md.
Rename this file and rewrite the body for your plugin.

Targeting Claude Code instead? Use agents/<your-plugin-name>.md (no `.agent`
infix) — `tools` becomes optional there. Delete whichever of the two agent
formats you don't need; an agent and a skill (see skills/example-skill/) can
also coexist in the same plugin.
-->

# Your Agent Name

<!-- Describe the agent's role in one or two sentences. -->

## Startup

<!-- What does the agent say/do at the start of a session? What does it list as available? -->

## Workflow

<!-- Step-by-step: how does the agent gather context, decide what to do, and produce its output? -->

## Constraints

<!-- Hard rules the agent must never break (e.g. always confirm before saving, never guess when context is missing). -->
