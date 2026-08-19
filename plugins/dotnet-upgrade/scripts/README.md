# Upgrade hook scripts

This folder holds the optional pre/post-upgrade hook scripts referenced by `config/upgrade-agent.md`:

```yaml
hooks:
  preUpgrade:
    - ./scripts/pre-upgrade-validate.ps1
  postUpgrade:
    - ./scripts/post-upgrade-build.ps1
```

## Contract

- Hooks run **per batch** (not per run).
- `preUpgrade` runs before Phase C edits for that batch; `postUpgrade` runs after the batch's commit step.
- Hooks must exit with code `0` on success. Any non-zero exit:
  - blocks the rest of that batch's components (in `preUpgrade`)
  - is recorded in `docs/upgrade-notes.md` as a hook failure (in `postUpgrade`)
- Hooks must not modify CI secrets or deployment configuration.

## Suggested scripts (none mandatory)

| File                       | When to use                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------ |
| `pre-upgrade-validate.ps1` | Verify clean working tree, branch is correct, no uncommitted changes.                      |
| `backup-config.ps1`        | Snapshot `global.json` / `Directory.Packages.props` to a local backup folder before edits. |
| `post-upgrade-build.ps1`   | Run a full solution build outside the batched scope for confidence.                        |
| `post-upgrade-report.ps1`  | Copy the consolidated batch report to a shared location.                                   |

## Authoring tips

- PowerShell-friendly (we run on Windows): use `pwsh` syntax — `$env:VAR`, `Test-Path`, etc.
- Take the component path as the first arg; emit human-readable progress to stdout.
- Keep them idempotent and side-effect-light.
