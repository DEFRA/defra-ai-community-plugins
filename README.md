# defra-ai-community-plugins

[![Validate](https://github.com/DEFRA/defra-ai-community-plugins/actions/workflows/validate.yml/badge.svg)](https://github.com/DEFRA/defra-ai-community-plugins/actions/workflows/validate.yml)

A community-run marketplace of [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing)
and Claude Code plugins for Defra teams — for plugins that don't meet, or
don't need, the bar of the official
[`defra-ai-plugins`](https://github.com/DEFRA/defra-ai-plugins) marketplace.

## 1. Quick overview

**What is this?** A place for Defra teams to publish their own Copilot CLI /
Claude Code agents and skills, reviewed once by the AI dev team (AICE) and then
owned by the contributing team from there on.

**How it differs from the official repo:**

|               | [`defra-ai-plugins`](https://github.com/DEFRA/defra-ai-plugins) (official)   | `defra-ai-community-plugins` (this repo)                                               |
| ------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Maintained by | AICE, on an ongoing basis                                                     | The contributing team, after AICE's initial review                                      |
| Bar to entry  | High — schema validation, CI, evals encouraged/becoming mandatory, docs-sync | Lighter — schema validation and CI, evals optional                                     |
| Best for      | Plugins meant to become a durable, org-wide standard                         | Plugins useful now, team-specific, experimental, or not yet ready for the official bar |

**Who should use it:** any Defra team with a useful Copilot CLI or Claude Code
plugin that isn't destined for, or doesn't yet meet the bar of, the official
marketplace. A plugin can always be proposed to the official repo later once
it's proven itself here.

## 2. Community support disclaimer

> **Read this before you contribute or install anything from here.**

- **Community-maintained, not AICE-maintained.** AICE reviews every pull
  request as a one-time quality gate. Once merged, the **contributing team**
  owns the plugin — bug fixes, updates, compatibility with new CLI versions,
  everything.
- **What to expect:** a structural review against the [Standards
  Checklist](#6-standards-checklist) below, within roughly 10 UK working days
  (see [CONTRIBUTING.md](CONTRIBUTING.md)).
- **What NOT to expect:** AICE fixing bugs, adding features, or upgrading a
  plugin on your behalf. If a plugin breaks, see the [FAQ](#7-faq).
- **Security issues are the exception** — see [SECURITY.md](SECURITY.md) for
  how those are triaged, including what happens if a maintaining team doesn't
  respond.

## 3. Getting started

**Prerequisites:**

| Tool                                        | Why                                                       |
| ------------------------------------------- | --------------------------------------------------------- |
| `git`                                       | To fork, clone, and branch                                |
| Node.js (see [`.nvmrc`](.nvmrc)) + `npm`    | Runs the repo validators (`npm test`)                     |
| `copilot` CLI or Claude Code CLI (optional) | To test-drive a plugin locally before or after installing |

**Repo setup:**

```sh
git clone https://github.com/<your-fork>/defra-ai-community-plugins.git
cd defra-ai-community-plugins
npm install
```

**Local development:**

```sh
npm run lint      # lint the validator scripts
npm run format    # check formatting
npm test          # run all structural validators
```

Optional — activate the tracked pre-commit hook so Prettier formats the repo
on every commit (one-time, per checkout):

```sh
git config core.hooksPath .githooks
```

## 4. Creating a plugin

Start by copying the scaffold:

```sh
cp -r plugins/_template plugins/<your-plugin-name>
```

**Required files:**

- `plugin.json` — the manifest (schema: [`schemas/plugin.schema.json`](schemas/plugin.schema.json))
- `README.md` — overview, what it provides, install commands
- One entry point in whichever format matches your target CLI:
  - `agents/<name>.agent.md` (Copilot custom agent)
  - `agents/<name>.md` (Claude Code agent)
  - `skills/<name>/SKILL.md` (works across Claude Code, Codex, Copilot CLI)

**Code standards:** where your plugin touches code generation, reference
[Defra's software development standards](https://github.com/DEFRA/software-development-standards)
and, for frontend work, the GOV.UK Design System and WCAG 2.2 AA — the same
standards the official repo's plugins encode.

**Documentation requirements:** your plugin's `README.md` must explain what
it does, when to use it, and give copy-pasteable install commands (see
`plugins/_template/README.md` for the expected shape).

**Testing expectations:** `npm test` must pass from the repo root before you
open a PR. Behavioural evals (asserting on what the agent actually produces)
are optional and encouraged, not required — see
[CONTRIBUTING.md](CONTRIBUTING.md#adding-a-new-plugin) for a reference
pattern if you want to build one.

Full step-by-step walkthrough: [CONTRIBUTING.md](CONTRIBUTING.md).

## 5. Contribution workflow

1. **Fork the repo** and create a branch: `feature/<plugin-name>`
2. **Build your plugin** following §4 above and the [Standards Checklist](#6-standards-checklist)
3. **Submit a PR** using the template, with the checklist filled in
4. **AICE review** — a structural check against the checklist below, aiming
   for an initial response within ~10 UK working days
5. **Approval → you merge** — once AICE approves, the contributing team
   merges their own PR; AICE isn't a bottleneck for day-to-day merges

## 6. Standards checklist

What AICE checks at review time (and what `npm test` enforces automatically
where possible):

- **Code structure** — plugin folder mirrors `plugins/_template/`; `plugin.json`
  passes schema validation; entry-point file matches one of the three
  supported formats
- **Naming conventions** — kebab-case `name`, matching the directory name and
  the `marketplace.json` entry; `marketplace.json` (both copies) sorted
  alphabetically
- **Documentation completeness** — plugin `README.md` has an overview, what
  it provides, and install commands
- **Testing coverage** — `npm test` passes locally; evals present and
  passing if you've added them
- **Security/safety** — no secrets, credentials, or real personal data in
  examples or fixtures; licence declared in `plugin.json`; the plugin
  declares any same-repo `dependencies` it relies on so missing-skill
  references are caught automatically

## 7. FAQ

**What happens if a plugin breaks?**
Open a bug-report issue tagged against the plugin. It routes to the
maintaining team named in `plugin.json#author` — not to AICE.

**Can AICE update my plugin?**
Not by default. AICE's role is the initial review; see the [Community Support
Disclaimer](#2-community-support-disclaimer). If your team can't maintain a
plugin any more, open an issue so it can be flagged or removed from
`marketplace.json`.

**Compatibility — Copilot CLI vs Claude Code?**
Both are supported entry-point formats (see §4). A plugin can ship a Copilot
agent, a Claude Code agent, a skill, or several of these together.

**Can my plugin move to the official repo later?**
Yes — that's an explicit path. Once a plugin has proven itself here, propose
it to [`defra-ai-plugins`](https://github.com/DEFRA/defra-ai-plugins) via
their plugin-proposal process, meeting their (higher) bar at that point.

## References

- [Defra software development standards](https://github.com/DEFRA/software-development-standards)
- [Defra AI SDLC playbook](https://defra.github.io/defra-ai-sdlc/)
- [Official `defra-ai-plugins` marketplace](https://github.com/DEFRA/defra-ai-plugins)
- [GitHub Copilot CLI plugin docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing)

## Licence

Open Government Licence v3.0 by default. See [LICENSE](LICENSE) — individual
plugins may declare a different SPDX licence, see [CONTRIBUTING.md](CONTRIBUTING.md).
