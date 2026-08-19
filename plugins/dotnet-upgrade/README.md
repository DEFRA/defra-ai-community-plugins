# dotnet-upgrade

A GitHub Copilot custom agent (`@dotnet-upgrade`) that automates end-to-end
.NET framework upgrades across multiple solutions. It batches upgrades,
provides human-in-the-loop checkpoints, reverts failures automatically, and
produces structured audit reports with per-component commits.

## What it provides

- A custom agent (**`dotnet-upgrade`**) that orchestrates a batched,
  multi-solution .NET upgrade run — discovery, dependency modernization,
  TFM/package edits, Azure Functions Isolated alignment, build/test with
  auto-fix, revert-on-failure, and final reporting.
- A Copilot Chat invocation prompt (`prompts/dotnet-upgrade.prompt.md`) with
  quick verbs: `assess`, `preview`/`dry-run`, `upgrade`, `resume`,
  `single <path>`.
- Seven phase skills under `skills/` that the agent invokes in order:
  `dotnet-upgrade-assessment`, `dotnet-inventory`, `dotnet-dependency-modernize`,
  `dotnet-upgrade`, `dotnet-functions-isolated`, `dotnet-build-test-fix`,
  `dotnet-upgrade-reporting`.
- Read-only report templates under `docs/` and a runtime config schema at
  `config/upgrade-agent.md` — edit this before every run to set
  `targetDotnetVersion`, `componentPaths`, `batchSize`, and other inputs.

## Prerequisites

- VS Code or Visual Studio 2022+ with the GitHub Copilot extension.
- .NET SDK matching `targetDotnetVersion` (default `net10.0`).
- Access to your organisation's internal NuGet feed, if upgrading projects
  that depend on private packages.
- PowerShell 7+ (`pwsh`) on `PATH` if using the optional pre/post-upgrade
  hook scripts described in `scripts/README.md`.

## Install

From the marketplace:

```sh
copilot plugin marketplace add DEFRA/defra-ai-community-plugins
copilot plugin install dotnet-upgrade@defra-ai-community-plugins
```

For Claude Code, run these inside an interactive session (they are slash
commands, not shell commands):

```text
/plugin marketplace add DEFRA/defra-ai-community-plugins
/plugin install dotnet-upgrade@defra-ai-community-plugins
```

From a local checkout (for development):

```sh
copilot plugin install ./plugins/dotnet-upgrade
```

## Use

1. Edit `config/upgrade-agent.md` to set `targetDotnetVersion`,
   `componentPaths` (the `.sln`/`.csproj` files to upgrade), `batchSize`, and
   any other runtime inputs.
2. Invoke the agent in Copilot Chat with `@dotnet-upgrade`, then use one of
   the quick verbs from `prompts/dotnet-upgrade.prompt.md`:
   - `assess` — read-only assessment report, then stop.
   - `preview` / `dry-run` — discovery report + planned-changes diff, no
     writes, branches, or commits.
   - `upgrade` — full run: gates, batched phases, per-component commits.
   - `resume` — continue a partially upgraded scope.
   - `single <path>` — upgrade a single project.
3. The agent pauses at human-in-the-loop gates (solution selection,
   pre-flight state check, dry-run sign-off, branch approval, commit
   approval) — respond to each prompt to continue.
4. Review generated artefacts under `docs/` (inventory, package
   replacements, upgrade notes, manual-review list, batch reports, final
   report) after each run.

The agent never pushes, opens PRs, or merges automatically — see
`agents/dotnet-upgrade.agent.md` for the full guardrails.

## Standards this plugin follows

- [Defra software development standards](https://github.com/DEFRA/software-development-standards)

## Licence

Open Government Licence v3.0. See [LICENSE](../../LICENSE).
