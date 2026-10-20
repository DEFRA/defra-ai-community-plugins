# code-quality

A GitHub Copilot custom agent (`code-quality`) that generates the CCTS Code
Quality Report from already-exported Sonar (SonarQube / SonarCloud) data. It
presents Red-Amber-Green (RAG) indicators, compliance gaps, and required
corrective actions as a static HTML governance report. It does not talk to
the Sonar server directly — the required `data-files/` are produced by an
external Sonar data pipeline (a separate repo), not this plugin.

## What it provides

- A custom agent (**`code-quality`**) that orchestrates two skills in
  sequence, then prints instructions to serve the final HTML report.
- A Copilot Chat/CLI invocation prompt (`prompts/code-quality.prompt.md`)
  that registers `/code-quality`.
- Two skills under `skills/`: `code-repo-maintenance-check` (sonarcloud
  repository-hygiene insights and Sonar licence-cost intelligence) and
  `code-assurance-rag` (per-group `Green`/`Amber`/`Red` compliance rating).
- Two standalone scripts (`scripts/process_sonar_metrics.py`,
  `scripts/process_assurance_rag.py`) — the single entry point each skill
  runs through; both use only the Python standard library.

## Prerequisites — input data files

This plugin does not fetch data from Sonar itself. Run the external Sonar data pipeline (separate repo) first, then copy its output into `data-files/` at this plugin's workspace root (see
[agents/copilot-instructions.md](agents/copilot-instructions.md) for the
full variable table):

- `data-files/sonar_repo_metrics.json`
- `data-files/all_groups_report.json`
- `data-files/project_group_map.json`

Sample versions of these files are already shipped under `data-files/` so
you can test the agent without running the external pipeline with 
currently shipped files that contains dummy data, not real Sonar output.


## Install

From the marketplace:

```sh
copilot plugin marketplace add DEFRA/defra-ai-community-plugins
copilot plugin install code-quality@defra-ai-community-plugins
```

From a local checkout (for development):

```sh
copilot plugin install ./plugins/code-quality
```

## Use

### From the Copilot CLI

1. Invoke the agent via Copilot CLI — either:

   a. **Non-interactive (recommended)** — runs straight through with no prompts:
      
      ```sh
      gh auth login
      gh copilot -- -C plugins/code-quality -p "/code-quality" --trust-folder --allow-all-tools --no-ask-user
      ```
      
   b. **Interactive** — type `/code-quality` once the session is ready; in
      this mode you'll need to approve a folder-trust prompt and each shell
      command the agent asks to run:
      
      ```sh
      gh auth login
      gh copilot -- -C plugins/code-quality
      ```

   Both invocations route through `prompts/code-quality.prompt.md` to the
   same agent. This plugin is CLI-only — it's invoked via `copilot
   plugin install`

2. Review the task checkpoints the agent prints as it runs: confirming the data files, running `code-repo-maintenance-check`, running `code-assurance-rag`, then resolving the path to serve `governance_report.html` locally.

3. View the final report by serving `data-files/` and opening it in a
   browser, e.g.:
   ```sh
   cd data-files && python -m http.server 8000
   ```
   then open `http://localhost:8000/governance_report.html`.



## Standards this plugin follows

- [Defra software development standards](https://github.com/DEFRA/software-development-standards)

## Maintainer

Owned by: Defra AI Community Engineering (AICE) — see `plugin.json#author`.
AICE reviews this plugin but does not commit to ongoing maintenance; see the
Community Support Disclaimer in the marketplace root
[README.md](../../README.md).