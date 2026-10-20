---
agent: code-quality
name: code-quality
description: Invoke the code-quality agent to generate the CCTS Code Quality Report from already-exported Sonar data files.
---

# /code-quality — invocation prompt

Use this prompt to drive the `code-quality` agent from VS Code Copilot Chat or GitHub.com Copilot Chat or any other compatible interface.

## Default flow

1. Task 0 — confirm `data-files/sonar_repo_metrics.json`, `data-files/all_groups_report.json`, and `data-files/project_group_map.json` exist.
2. Task 1 — run the `code-repo-maintenance-check` skill and write `ai_insights` back to `sonar_repo_metrics.json`.
3. Task 2 — run the `code-assurance-rag` skill and write `status` per group back to `all_groups_report.json`.
4. Task 3 — resolve `data-files/`'s absolute path and print instructions to serve `governance_report.html` locally.

## Outputs

- `data-files/sonar_repo_metrics.json` (updated in place)
- `data-files/all_groups_report.json` (updated in place)
- Instructions to serve `data-files/governance_report.html`

See `agents/code-quality.agent.md` for the full task breakdown and guardrails.
