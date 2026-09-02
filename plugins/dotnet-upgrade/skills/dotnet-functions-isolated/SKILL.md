---
name: dotnet-functions-isolated
description: Validates and aligns Azure Functions v4 Isolated Worker projects with target .NET — checks trigger/binding packages, host.json bundle, middleware patterns, and DI/startup pattern.
---

# dotnet-functions-isolated (Phase D — pre-build)

## Goal

Validate and (minimally) align Functions Isolated projects with `targetDotnetVersion` **before** Phase E build/test runs, so structural Functions issues (host.json bundle, Program.cs pattern, worker SDK swap) don't masquerade as cryptic build errors.

## Inheritance

Runtime inputs, scope rules, internal-feed policy, and guardrails come from **[../../agents/dotnet-upgrade.agent.md](../../agents/dotnet-upgrade.agent.md)**. Only processes projects classified as `Azure Functions Isolated` by `dotnet-inventory`.

## Validation flow

1. **Isolated model confirmed**
   - Must NOT use `Microsoft.NET.Sdk.Functions`.
   - Must use `Microsoft.Azure.Functions.Worker.Sdk`.
2. **Project basics**
   - `TargetFramework` = `targetDotnetVersion`.
   - `OutputType` = `Exe`.
3. **Host/runtime config**
   - `host.json` extension bundle: `[4.*, 5.0.0)`.
   - `local.settings.json` includes `FUNCTIONS_WORKER_RUNTIME=dotnet-isolated`.
4. **Trigger / binding packages**: compatible with target TFM (see `../dotnet-upgrade/references/net10-functions-changes.md` when `net10.0`).
5. **Startup pattern in `Program.cs`**
   - Use either `ConfigureFunctionsWorkerDefaults()` OR `ConfigureFunctionsWebApplication()`, never both.
6. **Middleware / telemetry** registrations validated when present.
7. Apply **minimal** targeted fixes only when needed.

## Common worker extensions to check

HTTP, HTTP+AspNetCore, Timer, Service Bus, Storage, Event Hubs, Cosmos DB.

## Output

- `docs/upgrade-notes.md`
- `docs/upgrade-report.md` → "Azure Functions Compatibility" section

## Handoff

After Phase D validation/alignment → Phase E (`dotnet-build-test-fix`) builds and tests the now-structurally-correct project.
