---
name: dotnet-upgrade
description: Applies the .NET TFM upgrade (Phase C) across classified project types — ASP.NET Web API, Azure Functions isolated, and class/test libraries — by editing TFMs, SDK pins, and package versions per the modernize plan.
---

# dotnet-upgrade (Phase C executor)

## Goal
Apply the minimal, auditable set of `.csproj` / `global.json` / `Directory.Packages.props` / package edits that move selected components to `targetDotnetVersion`.

## Inheritance
Runtime inputs, scope rules, internal-feed policy, and guardrails come from **[../../agents/dotnet-upgrade.agent.md](../../agents/dotnet-upgrade.agent.md)**. Honour `dryRun` from config — if true, **emit a diff preview only and exit** (no writes).

## References for breaking changes
Microsoft docs for `targetDotnetVersion`. For `net10.0` upgrades, also consult `./references/`:
- `net10-breaking-changes.md`
- `net10-aspnet-changes.md`
- `net10-functions-changes.md`

## Phase-C actions
1. Update `global.json` SDK pin to a compatible SDK for `targetDotnetVersion`.
2. Update project TFMs:
   - `TargetFramework` → `targetDotnetVersion`
   - `TargetFrameworks` → keep multi-targeting intent; drop obsolete TFMs only when inventory/assessment confirms.
3. Apply package updates from `docs/package-replacements.md`.
4. If CPM is used, change versions in `Directory.Packages.props` (no per-project duplication).
5. For internal packages, use feed-first readiness; never clone external repos.
6. Project-type adjustments:
   - ASP.NET (`Microsoft.NET.Sdk.Web`): align ASP.NET / Auth / OpenAPI / EF packages.
   - Azure Functions Isolated: align worker/runtime packages and host/local settings (see `dotnet-functions-isolated` for validation).
   - Class libraries / test projects: align TFM and package set.

## Minimal-edit rules
- Smallest safe change set.
- Preserve existing architecture unless the upgrade requires change.
- No new frameworks/patterns without evidence.
- Every package change explicit and traceable.

## Output / audit
- `docs/package-replacements.md` — every version change.
- `docs/upgrade-notes.md` — TFM/SDK edits, blockers, deviations.

## Handoff
After edits → `dotnet-build-test-fix` (Phase D). If `dotnet-build-test-fix` fails and `revertOnFailure: true`, the agent reverts this component's changes.
