---
name: dotnet-upgrade-reporting
description: Produces the final upgrade report and the per-run consolidated batch summary covering scope, project outcomes, package changes, validation results, Functions compatibility, blockers, manual-review items, and recommended next actions.
---

# dotnet-upgrade-reporting (Phase F)

## Goal

Write two artefacts:

1. `docs/upgrade-report.md` — overall final summary for the run.
2. `docs/upgrade-reports/<yyyyMMdd>.md` — consolidated batch report (one per run) covering all components attempted, outcomes, blockers, manual actions.

## Inheritance

Runtime inputs, scope rules, and guardrails come from **[../../agents/dotnet-upgrade.agent.md](../../agents/dotnet-upgrade.agent.md)**.

## Evidence sources

- `docs/upgrade-inventory.md`
- `docs/package-replacements.md`
- `docs/upgrade-notes.md`
- `docs/manual-review-list.md`
- Build/test outcomes from Phase D
- Per-component commit metadata (branch name + commit SHA when available)

## Steps

1. Summarise per-project outcomes: type, from-TFM, to-TFM, status (`Done` / `Partial` / `Blocked` / `Reverted` / `Skipped`).
2. Summarise package actions: total changes, breaking updates, replacements/removals, internal-package blockers.
3. Summarise validation: build/test pass-fail, iteration counts, key failures.
4. If Functions projects exist, include compatibility summary.
5. List unresolved blockers / risks with impact and next action.
6. Source-control summary: branches created, commits (SHAs), explicit note that **no push/PR/merge** was performed.
7. Manual-review items (from `manual-review-list.md`) and recommended next actions.

## Required sections (both reports)

1. Upgrade Scope
2. Project Outcomes
3. Package Changes
4. Build and Test Validation
5. Azure Functions Compatibility _(only if applicable)_
6. Blockers and Risks
7. Manual Review Items
8. Source-Control Summary
9. Recommended Next Actions

## Tables

```markdown
## Project Outcomes

| Project | Type | From TFM | To TFM | Status | Branch | Commit | Notes |
| ------- | ---- | -------- | ------ | ------ | ------ | ------ | ----- |

## Package Changes

| Project | Package | Old Version | New Version | Change Type | Reason |
| ------- | ------- | ----------- | ----------- | ----------- | ------ |

## Build and Test Validation

| Unit | Build | Test | Iterations | Notes |
| ---- | ----- | ---- | ---------- | ----- |

## Blockers and Risks

| Project | Issue | Impact | Attempted Fix | Next Action |
| ------- | ----- | ------ | ------------- | ----------- |

## Manual Review Items

| Component | Reason | Last Error | Files Reverted | Next Action |
| --------- | ------ | ---------- | -------------- | ----------- |
```

## Quality

- Observed evidence only; no fabricated data.
- Keep package detail aligned with `docs/package-replacements.md`.
- Always state: **no automatic push / PR / merge performed.**
