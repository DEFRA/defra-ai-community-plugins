---
name: code-quality
description: Generate an automated Code Quality Report for the CCTS team covering Code Repository Maintenance and Code Assurance. Analyse code hygiene, maintainability, technical-debt, and LOC metrics from the Sonar server to monitor repository health and ensure compliance with allocated LOCs. Present the metrics using Red-Amber-Green (RAG) indicators , compliance gaps, and required corrective actions.
argument-hint: "/code-quality"
tools: [view, edit, create, glob, grep, bash, powershell]
model: Claude Sonnet 5 (copilot)
---

# Code Quality Agent

**Invocation handle:** `/code-quality` (see [prompts/code-quality.prompt.md](../prompts/code-quality.prompt.md))

## Tasks

Every task below, and every step inside the skills it invokes, ends with a `Checkpoint:`. Per the Guardrails rule in [copilot-instructions.md](../copilot-instructions.md), print that checkpoint's checklist in the chat — ticking `[ok]`/`[x]` only for what you actually verified — before moving to the next task. Do not defer all checkpoints to the end.

### Task 0: Confirm the data files exist
- Files: `$sonar_repo_metrics_file`, `$all_group_report_file`, `$group_to_project_mapping` (see `data-files/` table in [copilot-instructions.md](../copilot-instructions.md))
- Checkpoint: all three exist — print `[ok]`/`[x]` per file
- If any are missing, stop and report which — do not try to generate them

### Task 1: Invoke the `code-repo-maintenance-check` skill
- Print every step's checkpoint from that skill's SKILL.md as they pass (Step 0 read, Step 1 cost, Step 2/3 write), not just a final summary
- Checkpoint: `$sonar_repo_metrics_file` updated (`ai_insights` written) — `narrative` present **and** every applicable `<base>_insights`/`<base>_action` pair from the skill's field table is populated (or legitimately empty per the persona's no-evidence rule)

### Task 2: Invoke the `code-assurance-rag` skill
- Print every step's checkpoint from that skill's SKILL.md as they pass (Step 0 groups, Step 1 read, Step 2 classify, Step 3 write), per group
- Checkpoint: `$all_group_report_file` updated (`status` per group, deterministically computed by `--stage classify` — this skill never produces `path_to_green` or any narrative field)

> **Run sequentially:** Only start Task 2 after Task 1 has fully completed. Do NOT run the two skills in parallel — wait for the `code-repo-maintenance-check` skill to finish writing all its output before invoking `code-assurance-rag`.

### Task 3: Final Validation
- Checkpoint: `RESOLVED_OUTPUT_DIR` resolved and success message printed
- This task's output is **appended after** the printed checkpoint trail from Tasks 0–2 — it never replaces or hides them
Resolve the absolute path by running this command and capturing its printed output into a variable called `RESOLVED_OUTPUT_DIR`:
```bash
python -c "import os; print(os.path.abspath('data-files'))"
```

Then output **exactly** this success message, replacing `{RESOLVED_OUTPUT_DIR}` with the actual absolute path printed by the command above.Do NOT output the literal text `{RESOLVED_OUTPUT_DIR}` or `<OUTPUT_DIR_ABS>` — you must substitute the real path:

```
Agent execution is successful.

To view the report:
  Open a new terminal and run:
  - cd "{RESOLVED_OUTPUT_DIR}"
  - python -m http.server 8000

Then open in your browser: http://localhost:8000/governance_report.html
```

Do **NOT** ask whether to commit to git. Do **NOT** ask what to do next. Stop here.