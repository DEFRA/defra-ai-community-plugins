# Upgrade Agent Inputs

Runtime inputs for the .NET upgrade agent. Loaded on every invocation.
The orchestrator (`agents/dotnet-upgrade.agent.md`) reads this file; skills inherit values from it.

---

## Schema (all keys)

| Key | Type | Default | Purpose |
|---|---|---|---|
| `targetDotnetVersion` | TFM | `net10.0` | Target framework moniker |
| `componentPaths` | list | _required_ | `.sln`/`.csproj`/folder roots in execution order | 
| `batchSize` | int | `3` | Components per batch (review checkpoint cadence) |
| `exclusions` | list | `[]` | Glob/path patterns to skip |
| `hooks.preUpgrade` | list | `[]` | Scripts run before each batch |
| `hooks.postUpgrade` | list | `[]` | Scripts run after each batch | 
| `internalNugetFeedUrl` | url | _see below_ | Private feed for internal package checks | 
| `internalNugetSourceName` | string | `Defranuget` | NuGet source alias | 
| `dryRun` | bool | `false` | Produce discovery + diff preview only; no file writes, no branches | 
| `branchingStrategy` | enum | `component` | `component` = one branch per component; `batch` = one branch per batch | 
| `branchNamingTemplate` | string | `upgrade/{targetTfm}/{component}-{yyyyMMdd}` | Template tokens: `{targetTfm}`, `{component}`, `{batchIndex}`, `{yyyyMMdd}` | 
| `commitMessageTemplate` | string | _see below_ | Header + structured body sections |
| `revertOnFailure` | bool | `true` | If build/test fails, revert component's changes and move it to manual review |
| `manualReviewListPath` | path | `docs/manual-review-list.md` | Where reverted/blocked components are recorded | 
| `consolidatedReportPath` | path | `docs/upgrade-reports/{yyyyMMdd}.md` | Per-batch summary (one per run) |

---

## Example: full configuration

```yaml
targetDotnetVersion: net10.0

componentPaths:
  - C:\Defra\Defra.Dotnet.Sample1\Defra.DotNet.Sample1.sln
  - C:\Defra\Defra.Dotnet.Sample2\Defra.DotNet.Sample2.sln
  - C:\Defra\Defra.Dotnet.Sample3\Defra.DotNet.Sample3.sln
  - C:\Defra\Defra.Dotnet.Sample4\Defra.DotNet.Sample4.sln

batchSize: 3

exclusions:
  - "**/*.sqlproj"

hooks:
  preUpgrade: []
  postUpgrade: []

internalNugetFeedUrl: https://pkgs.dev.azure.com/defragovuk/_packaging/[defra_nuget_feed_name]/nuget/v3/index.json
internalNugetSourceName: Defranuget

dryRun: false
branchingStrategy: component
branchNamingTemplate: "upgrade/{targetTfm}/{component}-{yyyyMMdd}"

commitMessageTemplate: |
  chore({component}): upgrade to {targetTfm}

  Components upgraded: {component}
  Packages bumped: see docs/package-replacements.md
  Automated fixes: see docs/upgrade-notes.md
  Build: {buildStatus}
  Tests: {testStatus}
  Run log: {consolidatedReportPath}

revertOnFailure: true
manualReviewListPath: docs/manual-review-list.md
consolidatedReportPath: docs/upgrade-reports/{yyyyMMdd}.md
```

---

## Defaults applied when key is missing

- If a key is absent, the agent uses the default in the table above and notes the substitution in `docs/upgrade-notes.md`.
- If `componentPaths` is missing, the agent runs **Gate 0** to ask the user.
- If `dryRun: true`, **no** file writes, **no** branches, **no** commits — only discovery + diff preview.

---

## Token tokens for templates

`{component}` — component name (sln/csproj basename); `{targetTfm}` — e.g. `net10.0`;
`{batchIndex}` — 1-based; `{yyyyMMdd}` — UTC date; `{buildStatus}` / `{testStatus}` — `pass` | `fail` | `skipped`.
