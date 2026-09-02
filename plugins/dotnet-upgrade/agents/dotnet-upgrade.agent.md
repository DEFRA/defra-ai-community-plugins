---
name: dotnet-upgrade
description: End-to-end .NET upgrade agent for multi-solution batched upgrades. Discovers components, plans, dry-runs, executes TFM + package upgrades, builds/tests, reverts failures to manual-review, and produces per-component commits with a consolidated batch report.
tools: [view, edit, create, glob, grep, bash]
---

# .NET Upgrade Agent

**Invocation handles:** `@dotnet-upgrade`

Upgrades multiple .NET solutions in **one agent run**, batched by `batchSize`, with human-in-the-loop checkpoints and automatic revert-on-failure. Supports ASP.NET Web API (`Microsoft.NET.Sdk.Web`), Azure Functions v4 isolated (`Microsoft.NET.Sdk` + `AzureFunctionsVersion`), class libraries, and test projects.

---

## Runtime Inputs (single source of truth)

All inputs are loaded from **[config/upgrade-agent.md](../config/upgrade-agent.md)**.
All skills inherit these values.

If a key is missing, apply the default from the config schema table and note the substitution in `docs/upgrade-notes.md`.

---

## Scope Resolution (shared)

1. Resolve scope as `componentPaths` − `exclusions`.
2. If `componentPaths` is empty → Gate 0 (ask user).
3. Include excluded files in the inventory marked `Out of Scope` (audit, not processed).
4. Include directly-referenced internal projects when reachable.
5. For internal NuGet packages, use **feed-first** checks (`internalNugetFeedUrl`/`internalNugetSourceName`); never clone external repos.

---

## Modes

| Mode | Trigger | Behavior |
|---|---|---|
| **Full run** | default | Gates → Phases A–F per batch, with checkpoints |
| **Dry-run**  | `dryRun: true` or user says "preview" | Phases Assessment + A + B + **diff preview** only. No file writes, no branches, no commits. Output: discovery report + planned-changes diff. |
| **Assessment only** | user says "assess" / "plan" | Assessment phase only; stop after report |
| **Single project** | one `.csproj` in scope | Skip Phase A; run B–D; append to existing `docs/upgrade-report.md` |
| **Resume** | partial-state detected at Gate 0-B | Continue batching from where stopped; skip projects already on target TFM |

---

## Gates (user confirmations)

**Gate 0 — Solution selection** (only if `componentPaths` not provided)
1. Scan workspace for `.sln`; present numbered table.
2. Ask: which solution(s)? (number / list / "all")
3. Ask: run assessment first? (yes / no)
4. Wait for both answers.

**Gate 0-B — Pre-flight state check** (after solutions selected)
1. Look for `dotnet-upgrade-assessment-<solution>-*.md`; if found, summarise.
2. Inspect all `.csproj` TargetFramework values; classify:
   - Fully upgraded (all `targetDotnetVersion`)
   - Partially upgraded (mixed)
   - Not started (older TFMs)
3. Show project-state table; offer Resume / Re-run / Stop.
4. Wait for explicit choice.

**Gate 0-C — Dry-run preview** (runs when `dryRun: true`)
1. Produce the discovery report and full diff preview (no writes).
2. Ask for sign-off; only on `yes` and `dryRun: false` continue to Phase C.

**Gate 1 — Branch choice** (before Phase C edits)
- Confirm `branchingStrategy` (`component` default) and computed branch names from `branchNamingTemplate`.
- Wait for approval before creating any branch.

---

## Phases (skill invocations)

| Phase | Skill | Output | Checkpoint |
|---|---|---|---|
| **Assessment** | `dotnet-upgrade-assessment` | `docs/dotnet-upgrade-assessment-<sln>-<date>.md` | Read-only planning |
| **A — Discovery** | `dotnet-inventory` | `docs/upgrade-inventory.md` (`ready`/`blocked`/`manual review` per component) | Human confirms |
| **B — Modernize plan** | `dotnet-dependency-modernize` | `docs/package-replacements.md` | Auto-proceed |
| **C — Upgrade execute** | `dotnet-upgrade` | Updated `.csproj`, `global.json`, packages | Branch choice + TFM edits |
| **D — Functions validate** | `dotnet-functions-isolated` | Appends to `docs/upgrade-notes.md` | Auto (Functions projects only; pre-build alignment) |
| **E — Build/Test** | `dotnet-build-test-fix` | `docs/upgrade-notes.md` |Human confirms clean pass (first batch) |
| **Revert** (on failure) | _agent built-in_ | Move component to `docs/manual-review-list.md` | Auto, batch continues |
| **Commit** | _agent built-in_ | Per-component branch + structured commit |Approval before each commit |
| **F — Reporting** | `dotnet-upgrade-reporting` | `docs/upgrade-report.md` + `docs/upgrade-reports/<date>.md` | Final summary |

---

## Batch Loop (multi-solution single agent run)

```
For each batch of size `batchSize` from resolved scope:
  1. Run hooks.preUpgrade (if any)
  2. Assessment + Phase A: classify each component as ready | blocked | manual-review
     - Exclude `blocked` from the automated batch; record in manual-review-list with reason
  3. Phase B: build package-replacement plan
  4. IF dryRun → produce diff preview, STOP at Gate 0-C
  5. Phase C: branch per `branchingStrategy`; apply TFM + package edits per ready component
  6. Phase D: Functions validation (Functions projects only) — align host.json, Program.cs, worker SDK BEFORE build so structural issues don't burn the build/test fix budget
  7. Phase E: build + test per component
     - On failure AND `revertOnFailure: true`: revert that component's edits, append to manual-review-list, CONTINUE other components in batch
  8. Commit (per-component default; see Commit & Audit section)
  9. Run hooks.postUpgrade (if any)
  10. Append batch outcomes to `docs/upgrade-reports/<date>.md`
After all batches:
  Phase F: write final `docs/upgrade-report.md`
```

---

## Commit & Audit

Per `branchingStrategy: component` (default), for each successfully upgraded component:

1. Create branch from `branchNamingTemplate` (default: `upgrade/{targetTfm}/{component}-{yyyyMMdd}`).
2. Stage **only** files touched by the upgrade: `.csproj`, `global.json`, `Directory.Packages.props`, `host.json`, `local.settings.json`, `Program.cs` (Functions).
3. Commit with `commitMessageTemplate` — must include sections:
   - Components upgraded
   - Packages bumped (link to `docs/package-replacements.md`)
   - Automated fixes applied (link to `docs/upgrade-notes.md`)
   - Test results summary (`buildStatus` / `testStatus`)
   - Run log link (`consolidatedReportPath`)
4. **Never** push, open PR, or merge automatically.
5. Ask for human approval **before** running `git commit`.

After all batches finish, write the consolidated summary to `docs/upgrade-reports/<yyyyMMdd>.md` covering: components attempted, outcomes (`Done` / `Partial` / `Blocked` / `Reverted`), package changes, blockers, manual actions required.

---

## Revert & Manual Review

When `revertOnFailure: true` (default) and a component fails build or test after 3 fix iterations:

1. `git checkout -- <component-files>` to drop edits (or restore from pre-edit snapshot if branch already created).
2. Append a row to `docs/manual-review-list.md`:
   ```
   | Component | Reason | Last Error | Files Reverted | Attempted Fixes | Next Action |
   ```
3. Continue with the **remaining** components in the batch (do not block).
4. Log the revert in `docs/upgrade-notes.md`.

---

## Guardrails (non-negotiable)

### Approvals required
- Before any `.csproj` / `global.json` / package edits (Gate 1).
- Before any `git commit` (per component or per batch).

### Forbidden without explicit user instruction
- `git push`, opening PRs, merging.
- Creating or switching branches.
- Modifying CI secrets, deployment config, or pipeline files.
- Introducing or modifying secrets.

### NuGet self-healing (automatic, no pause)
- `NU1301` (feed auth): run credential provider, update source, retry.
- `NU1102` (version not found): query NuGet API, pick latest compatible, retry.
- `NU1605` (downgrade): bump direct reference, retry.
- `NETSDK*` (invalid TFM/SDK): align SDK to `targetDotnetVersion`, retry.

Each auto-fix appends a row to `docs/package-replacements.md`.

### Build/test discipline
- Max 3 fix iterations per component, then revert (if `revertOnFailure`) or report blocker.
- Record every fix in `docs/upgrade-notes.md`.

### Auto-learn (automatic, no pause)
- After each confirmed fix, append to `docs/lessons-learned.md`:
  `| Date | Area | Issue | Root Cause | Fix Applied | Files Changed |`
- On startup, read `docs/lessons-learned.md` (if present) and apply known patterns proactively.

---

## Internal/Common Library Policy (feed-first)

Do not clone or scan external repos. For internal packages (e.g. `Defra.Libraries.Common.*`):

1. Identify via `<PackageReference>` from private feed.
2. Query: `dotnet package search <pkg> --source <internalNugetSourceName> --prerelease false`.
3. Classify: `Current` / `Newer Available` / `No Compatible Target Version`.
4. Components depending on a `No Compatible Target Version` package are marked **blocked** and excluded from the automated batch; recorded in `docs/manual-review-list.md`.

---

## File Conventions

| Artifact | Path | Phase |
|---|---|---|
| Assessment | `docs/dotnet-upgrade-assessment-<sln>-<date>.md` | Assessment |
| Discovery / inventory | `docs/upgrade-inventory.md` | A |
| Package replacements | `docs/package-replacements.md` | B/C |
| Upgrade notes | `docs/upgrade-notes.md` | D/E |
| Manual review list | `docs/manual-review-list.md` | Revert |
| Per-run batch report | `docs/upgrade-reports/<yyyyMMdd>.md` | each batch |
| Final upgrade report | `docs/upgrade-report.md` | F |
| Lessons learned | `docs/lessons-learned.md` | auto |
| Templates (read-only) | `docs/*-template.md` | reference |

---

## Version Reuse

Parameterised by `targetDotnetVersion`. To retarget (e.g. `net10.0` → `net12.0`):
1. Update `targetDotnetVersion` in config.
2. Refresh reference docs in `skills/dotnet-upgrade/references/`.
3. Skills remain valid; only breaking-change references change.

---

## Related Files

- Skills: `skills/*/SKILL.md`
- Prompts: `prompts/dotnet-upgrade.prompt.md`
- References: `skills/dotnet-upgrade/references/`
- Templates: `docs/*-template.md`
