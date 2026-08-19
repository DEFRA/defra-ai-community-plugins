---
agent: dotnet-upgrade
name: dotnet-upgrade
description: Invoke the .NET upgrade agent for batched multi-solution upgrades, dry-run previews, or single-component upgrades.
---

# /dotnet-upgrade — invocation prompt

Use this prompt to drive the `dotnet-upgrade` agent from VS Code Copilot Chat or GitHub.com Copilot Chat or any other compatible interface.

## Quick verbs

| Verb                  | What it does                                                                                         |
| --------------------- | ---------------------------------------------------------------------------------------------------- |
| `assess`              | Run **Assessment only** — writes `docs/dotnet-upgrade-assessment-<sln>-<date>.md`, then stops.       |
| `preview` / `dry-run` | Force `dryRun: true` for this run — discovery report + diff preview, no file mutations, no branches. |
| `upgrade`             | Full run — gates, batched phases A–F, per-component commits.                                         |
| `resume`              | Continue a partially upgraded scope; skip components already on target TFM.                          |
| `single <path>`       | Upgrade one `.csproj` only; skip Phase A; append to existing report.                                 |

## Default flow

1. Loads inputs from `config/upgrade-agent.md`.
2. Gate 0 — if `componentPaths` empty, asks you to select solution(s).
3. Gate 0-B — pre-flight state check (resume / re-run / stop).
4. Gate 0-C — dry-run sign-off (when `dryRun: true`).
5. Phases: Assessment → A (Discovery, with readiness labels) → B (Modernize plan) → Gate 1 (branch choice) → C (TFM/package edits) → D (Functions validate, pre-build, Functions only) → E (Build/Test, max 3 cycles) → Revert if needed → Commit (per component) → F (Reporting).

## Outputs

- `docs/upgrade-inventory.md`
- `docs/package-replacements.md`
- `docs/upgrade-notes.md`
- `docs/manual-review-list.md`
- `docs/upgrade-reports/<yyyyMMdd>.md`
- `docs/upgrade-report.md`
- Per-component branch + structured commit

## Non-negotiable

- No `git push`, no PR creation, no merge — ever automatic.
- No edits without explicit approval at Gate 1.
- No `dryRun: false` writes until Gate 0-C is cleared (when dry-run was requested).

See `agents/dotnet-upgrade.agent.md` for full behaviour.
