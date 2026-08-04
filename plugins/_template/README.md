<!--
Template plugin README. Copy this whole plugins/_template/ directory to
plugins/<your-plugin-name>/, then replace every section below with your
plugin's real content. See CONTRIBUTING.md for the full walkthrough.
-->

# your-plugin-name

<!-- One paragraph: what does this plugin do, and what problem does it solve? -->

## What it provides

<!--
List what this plugin ships, e.g.:
- A custom agent (**`your-plugin-name`**) that ...
- A skill (**`example-skill`**) that ...
-->

## Prerequisites

<!--
If this plugin depends on another plugin in this same marketplace (declared
in plugin.json#dependencies), say so here and list the install order. Plugins
in this repo can only depend on other plugins in this repo — not on plugins
published only in the official defra-ai-plugins marketplace.
-->

## Install

From the marketplace:

```sh
copilot plugin marketplace add DEFRA/defra-ai-community-plugins
copilot plugin install your-plugin-name@defra-ai-community-plugins
```

For Claude Code, run these inside an interactive session (they are slash
commands, not shell commands):

```text
/plugin marketplace add DEFRA/defra-ai-community-plugins
/plugin install your-plugin-name@defra-ai-community-plugins
```

From a local checkout (for development):

```sh
copilot plugin install ./plugins/your-plugin-name
```

## Use

<!-- How does someone actually invoke this agent/skill once installed? -->

## Standards this plugin follows

<!--
Reference relevant standards, e.g.:
- Defra software development standards: https://github.com/DEFRA/software-development-standards
- GOV.UK Design System / WCAG 2.2 AA, if this plugin touches frontend code
-->

## Licence

Open Government Licence v3.0. See [LICENSE](../../LICENSE). If this plugin
uses a different SPDX licence, replace this section and add your own
`LICENSE` file in this directory.
