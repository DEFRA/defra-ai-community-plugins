---
name: dotnet-dependency-modernize
description: Analyses NuGet dependencies across selected projects for target .NET compatibility. Identifies deprecated, removed, vulnerable, or incompatible packages and produces docs/package-replacements.md.
---

# dotnet-dependency-modernize

## Goal
Write the package-replacement plan to `docs/package-replacements.md` — feeds Phase C (`dotnet-upgrade`) execution.

## Inheritance
Runtime inputs, scope rules, internal-feed policy, and guardrails come from **[../../agents/dotnet-upgrade.agent.md](../../agents/dotnet-upgrade.agent.md)**.

## Analysis steps
1. Collect `PackageReference`, `PackageVersion`, `ProjectReference`, CPM usage.
2. Per project (or solution):
   - `dotnet list <path> package --outdated`
   - `dotnet list <path> package --deprecated`
   - `dotnet list <path> package --vulnerable`
3. Internal packages: query `internalNugetFeedUrl` via `internalNugetSourceName`; compare current vs latest compatible.
4. Classify each package:
   - `Safe update`
   - `Breaking update`
   - `Replace`
   - `Remove`
   - `Rebuild internal`
5. If any project has a package with no target-compatible version, mark that project as `blocked` (for the agent's batch-exclusion logic).

## Output schema

```markdown
# Package Replacements — <date>

Target: <targetDotnetVersion>
Scope: <componentPaths>
Exclusions: <exclusions or none>

| Project | Package | Current Version | Recommended Version / Replacement | Category | Notes |
|---|---|---|---|---|---|
```

Include internal-feed rows with status: `Current` / `Newer Available` / `No Compatible Target Version`.

## CPM rules
If `Directory.Packages.props` exists:
- Manage version changes there.
- Do not add per-project `Version` unless intentionally overriding.

## Quality
- Plan/report only — do not edit `.csproj` here.
- Evidence-based, concise.
- Use `targetDotnetVersion` from config; never hardcode a TFM.
