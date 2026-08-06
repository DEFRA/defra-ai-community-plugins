# Contributing to defra-ai-community-plugins

Thanks for your interest in contributing. This repository is the Defra
**community** GitHub Copilot CLI / Claude Code plugin marketplace — a home
for plugins that don't meet, or don't seek, the bar of the official
[`defra-ai-plugins`](https://github.com/DEFRA/defra-ai-plugins) marketplace.

Anyone can propose and contribute a plugin. All changes go through GitHub
pull requests and are reviewed by the Defra AI dev team (AICE) as a quality
gate.

> **Maintenance model.** AICE reviews contributions but does **not** commit to
> maintaining what's merged. The contributing team owns their plugin going
> forward — bug fixes, updates, and compatibility all fall to them, not AICE.
> See the "Community Support Disclaimer" in [README.md](README.md) for the
> full picture.

## How the marketplace is organised

```
defra-ai-community-plugins/
├── .github/
│   ├── plugin/
│   │   └── marketplace.json          # the registry — every plugin must be listed here
│   └── workflows/
│       └── validate.yml              # CI: runs the validators on every PR
├── schemas/
│   ├── marketplace.schema.json
│   └── plugin.schema.json
├── scripts/                          # Node.js validators
└── plugins/
    ├── _template/                    # copy this to start a new plugin
    └── <plugin-name>/
        ├── plugin.json               # plugin manifest
        ├── README.md                 # plugin docs and install commands
        └── agents/
            └── <plugin-name>.agent.md
```

Each plugin is a self-contained directory under `plugins/`. The marketplace
registry (`.github/plugin/marketplace.json`, mirrored at
`.claude-plugin/marketplace.json`) lists every plugin and is the source of
truth for what's installable.

## Adding a new plugin

1. **Open a plugin proposal issue first.** Use the "Plugin proposal" issue
   template. This helps avoid duplicate work and gives AICE a chance to flag any
   concerns before you put effort in. It also asks who will maintain the
   plugin going forward — required, since AICE won't.

2. **Fork the repo and create a branch.** Use the conventional naming
   `feature/<plugin-name>` or `feature/<short-description>`.

3. **Copy `plugins/_template/` as a template.** Rename the folder to
   `plugins/<your-plugin-name>/`.

4. **Edit the manifest.** Update `plugins/<your-plugin-name>/plugin.json`:

   - `name` must match the directory name (kebab-case, ≤50 characters)
   - `description` is one sentence (≤500 characters)
   - `version` is `0.1.0` for a new plugin
   - `author`, `license`, `homepage`, `repository`, `keywords`, `category` as
     appropriate. `license` defaults to `OGL-UK-3.0`; if your team needs a
     different SPDX licence, set it here and add a `plugins/<your-plugin-name>/LICENSE`
     file with the full text.

5. **Edit the entry-point file.** Rename `agents/example-agent.agent.md` to
   match your plugin and rewrite the body. The validators support three
   entry-point formats — pick the one that matches your target CLI:

   - **Copilot custom agent** — `agents/<your-plugin-name>.agent.md`.
     Frontmatter must include `description` and a non-empty `tools` array.
   - **Claude Code agent** — `agents/<your-plugin-name>.md` (no `.agent`
     infix). Frontmatter must include `description`. `tools` is optional but,
     if present, must be an array of strings.
   - **Skill** (works for Claude Code, Codex, and Copilot CLI) —
     `skills/<your-plugin-name>/SKILL.md`. Frontmatter must include `name`
     (matching the parent directory) and `description`.

   Delete whichever example file(s) in `plugins/_template/` you don't need —
   an agent and a skill can coexist, or you can ship just one.

6. **Edit the plugin README.** Update `plugins/<your-plugin-name>/README.md`
   with what the plugin does, when to switch to it, and the install commands.

7. **Register the plugin.** Add an entry to `.github/plugin/marketplace.json`
   **and** the mirrored `.claude-plugin/marketplace.json`. Keep the `plugins`
   array sorted alphabetically by `name` in both files. The validator will
   fail if it isn't.

8. **Run the validators locally:**

   ```sh
   npm install     # first time only
   npm test
   ```

   All checks must pass before opening a PR.

9. **Evals are optional.** Not required to merge, and this repo doesn't ship
   a promptfoo harness like the official repo does — building one is a
   welcome addition if your team wants it, but not a bar to clear here. If
   you want a reference pattern, see `frontend-developer/evals/` in the
   official [`defra-ai-plugins`](https://github.com/DEFRA/defra-ai-plugins) repo.

10. **Open a pull request** using the PR template and fill in the checklist.

## Naming conventions

- Plugin names: kebab-case, lowercase letters / digits / hyphens, ≤50 characters
- Plugin directory name = `plugin.json#name` = `marketplace.json` entry name
- Entry-point file naming follows the chosen format (see step 5 above)
- `plugins/_template/` is scaffolding, not a plugin — it's excluded from
  validation and never registered in `marketplace.json`

## Validation rules

The `Validate` workflow runs five schema/structural checks. All must pass:

| Check                     | What it enforces                                                                                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `marketplace.json` schema | Required fields, kebab-case names, no duplicates, source paths start with `plugins/`                                                                                |
| `plugin.json` schema      | Required fields per plugin; name matches directory and marketplace entry                                                                                            |
| Entry-point frontmatter   | Per-format frontmatter rules (Copilot agent, Claude agent, or skill)                                                                                                |
| Cross-plugin refs         | Every skill named in an agent prompt resolves to the agent's own plugin or a plugin declared in `dependencies` — and dependencies must be plugins in this same repo |
| Alphabetical sort         | Marketplace plugins sorted by name                                                                                                                                  |

To auto-fix sorting:

```sh
npm run validate:fix
```

## Merge rights

AICE is a required reviewer via CODEOWNERS, but once a PR is approved, the
contributing team merges it themselves — AICE is not a click-merge bottleneck
for day-to-day contributions. (This is a GitHub branch-protection setting,
not something enforced by any file in this repo — flag to AICE if it isn't
configured that way yet.)

## Licence

By contributing, you agree that your contribution is licensed under the [Open
Government Licence v3.0](LICENSE) by default, or another SPDX licence you
declare in `plugin.json` alongside your own `LICENSE` file.

## Code of Conduct

This project follows the [Contributor Covenant v2.1](CODE_OF_CONDUCT.md). Please
be respectful and constructive in all interactions.

## Reporting security issues

Do NOT open a public issue for security vulnerabilities. See
[SECURITY.md](SECURITY.md) for the disclosure process.
