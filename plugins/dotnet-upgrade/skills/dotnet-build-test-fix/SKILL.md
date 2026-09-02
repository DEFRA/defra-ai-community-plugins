---
name: dotnet-build-test-fix
description: Runs dotnet build/test on upgraded components, applies targeted fixes for common breaking changes, iterates up to 3 times, and signals revert-or-blocker so the agent can move failed components out of the batch.
---

# dotnet-build-test-fix (Phase E)

## Goal

Drive each upgraded component to a clean build + test pass with minimal fixes. If unresolved after 3 cycles, signal failure so the agent can revert and continue the batch.

## Order assumption

Runs **after** Phase D (`dotnet-functions-isolated`). For Functions projects, structural alignment (host.json bundle, Program.cs startup pattern, worker SDK swap) is already in place — any remaining build errors should reflect real code/package issues, not predictable Functions structural ones.

## Inheritance

Runtime inputs, scope rules, and guardrails come from **[../../agents/dotnet-upgrade.agent.md](../../agents/dotnet-upgrade.agent.md)**.

## Execution flow

1. `dotnet build <path> --no-incremental -warnaserror:false`
2. Capture compile / SDK / NuGet errors.
3. Apply smallest targeted fix per error.
4. Rebuild and repeat.
5. After successful build: `dotnet test <path> --no-build --logger "console;verbosity=normal"`
6. Fix failing tests with minimal changes; re-run.

## Error triage (typical)

| Code                | Cause                  | Fix direction                                   |
| ------------------- | ---------------------- | ----------------------------------------------- |
| `CS0246` / `CS0234` | Missing namespace/type | Check package/reference/usings                  |
| `CS0619`            | Obsolete API           | Replace with supported API                      |
| `CS8602`            | Nullable flow          | Add null guard or use `GetRequiredService<T>()` |
| `NETSDK*`           | SDK/TFM mismatch       | Align SDK to `targetDotnetVersion`              |
| `NU1202` / `NU1701` | Incompatible package   | Update or replace via `package-replacements.md` |

## Common fix patterns

- `BinaryFormatter` → supported serialiser (`System.Text.Json`).
- `WebClient` → `HttpClient`.
- Nullable required-DI: prefer `GetRequiredService<T>()` over `GetService<T>()`.

## Iteration limit

- **Max 3 fix cycles** per component.
- After 3 failed cycles → return `FAILED` to the agent with the last error block. The agent then either reverts (default) or records a blocker.

```markdown
## Unresolved Build/Test Blockers

| Project | Error | Description | Attempted Fixes |
| ------- | ----- | ----------- | --------------- |
```

## Output / handoff

- `docs/upgrade-notes.md` — every fix and every blocker.
- `docs/upgrade-report.md` — final pass/fail per component.

Stop for human review after the **first** clean build/test pass in a run (agent's Phase-D checkpoint).
