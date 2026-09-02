---
name: dotnet-upgrade-assessment
description: Produces an evidence-based .NET upgrade assessment document for selected solutions and their internal/common library dependencies. Cross-checks package inventory, vulnerabilities, deprecated APIs, and shared-dependency risks.
---

# dotnet-upgrade-assessment

## Goal

Write `docs/dotnet-upgrade-assessment-<solution-name>-<YYYY-MM-DD>.md` from the read-only template at `docs/dotnet-upgrade-assessment-template.md`.

## Inheritance

Runtime inputs, scope rules, internal-feed policy, and guardrails are defined once in **[../../agents/dotnet-upgrade.agent.md](../../agents/dotnet-upgrade.agent.md)**. Inherit; do not redeclare.

## Steps

1. Discover `.sln`/`.csproj` metadata: `TargetFramework`, `TargetFrameworks`, SDK, `AzureFunctionsVersion`, `PackageReference`, `ProjectReference`.
2. Build direct package inventory:
   `Project | Package | Current Version | .NET Update Type | Notes`
3. `dotnet list package --vulnerable` → merge findings into Notes.
4. Scan deprecated/legacy patterns: `AzureServiceTokenProvider`, `AddAzureKeyVault`, `Microsoft.Extensions.Configuration.AzureKeyVault`, `Microsoft.Azure.Functions.Extensions`, `System.Data.SqlClient`, `WebClient`, `BinaryFormatter`, legacy test packages.
5. Internal feed cross-check (feed-first): classify each internal package as `Current` / `Newer Available` / `No Compatible Target Version`.
6. Produce definitive actions with file/method evidence.

## Allowed `.NET Update Type` values

- `Package only (to X.Y.Z)`
- `Package only (upgrade to X.Y+)`
- `Package only (rebuild internal)`
- `Code + Package`

## Required sections (mirror the template)

1. Repository Overview
2. Package Inventory (Direct)
3. Compatibility Assessment (Definitive)
4. Breaking Changes for .NET Upgrade
5. Vulnerability Findings
6. Deprecated / Legacy Scan
7. Common / Internal Library Status
8. Step-by-Step Upgrade Path
9. Microsoft Documentation Links

## Quality

- Evidence only — no speculation.
- Concrete versions over vague guidance.
- Mark blockers clearly (especially internal packages without target-compatible builds → feeds into the agent's `blocked`/manual-review flow).
- Short, no duplicated prose.
- Never modify `dotnet-upgrade-assessment-template.md`.
