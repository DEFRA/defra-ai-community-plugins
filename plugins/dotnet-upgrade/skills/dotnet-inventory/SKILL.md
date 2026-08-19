---
name: dotnet-inventory
description: Discovers and classifies all .NET projects in selected solutions, capturing SDK, TargetFramework, NuGet packages, project category, and upgrade-readiness status. Outputs docs/upgrade-inventory.md.
---

# dotnet-inventory

## Goal

Write `docs/upgrade-inventory.md` — the discovery report — with one row per project and a clear upgrade-readiness label.

## Inheritance

Runtime inputs, scope rules, and guardrails come from **[../../agents/dotnet-upgrade.agent.md](../../agents/dotnet-upgrade.agent.md)**.

## Data captured per project

From `.sln`, `.csproj`, `Directory.Build.props`, `Directory.Packages.props`, `global.json`:

- Name / path
- SDK (`Project Sdk`)
- `TargetFramework` / `TargetFrameworks`
- `AzureFunctionsVersion` (if present)
- `OutputType`
- `PackageReference` list
- `ProjectReference` list
- Test markers (`IsTestProject`, xUnit/NUnit/MSTest)
- CPM usage (from `Directory.Packages.props`)
- Internal NuGet status (via configured feed)

## Classification

| SDK / marker                                  | Type                     |
| --------------------------------------------- | ------------------------ |
| `Microsoft.NET.Sdk.Web`                       | ASP.NET Web API / MVC    |
| `Microsoft.NET.Sdk` + `AzureFunctionsVersion` | Azure Functions Isolated |
| Any SDK + test markers                        | Test Project             |
| `Microsoft.NET.Sdk` (other)                   | Class Library            |
| `*.sqlproj`                                   | Out of Scope             |

## Upgrade-readiness label

| Label                     | Meaning                                                                                                                                            |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| ✅ `ready`                | TFM upgrade can proceed automatically in this batch                                                                                                |
| ⚠️ `manual review needed` | Code touches deprecated APIs, multi-target requires user choice, or test framework needs attention                                                 |
| ⛔ `blocked`              | Internal/external package has no version compatible with `targetDotnetVersion`; excluded from automated batch and added to `manual-review-list.md` |
| ⏭ `out of scope`          | Excluded by config or unsupported SDK (e.g. `.sqlproj`)                                                                                            |

## Output schema

```markdown
# Upgrade Inventory — <date>

## Scope

Target: <targetDotnetVersion>
Components: <componentPaths>
Exclusions: <exclusions or none>
Global SDK: <global.json or "not pinned">
CPM: <yes/no>

## Projects

| Project | Type | Path | Current TFM | SDK | Key Packages | Readiness | Reason |
| ------- | ---- | ---- | ----------- | --- | ------------ | --------- | ------ |

## Upgrade Risk Flags

- Multi-target frameworks
- Platform-specific TFMs (e.g. netX.Y-windows)
- Legacy/incompatible package markers
- Out-of-scope projects
```

## Quality

- Inventory only — no project edits in this phase.
- Use `targetDotnetVersion` from config; never hardcode a TFM.
- Compact, evidence-based.
