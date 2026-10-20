---
name: code-assurance-rag
description: Evaluate CCTS code-quality metrics against defined thresholds and generate an automated RAG-based assurance report highlighting compliance status.
---

# Code Assurance RAG

**Before anything else:** open and read the file [code-assurance-rag.md](persona/code-assurance-rag.md) in full. Its role, context, and constraints apply to every step in this file — do not start the workflow below without reading it.

Runbook for the code-assurance-rag skill: per group, read the evidence, calculate the RAG status, then write it back to the JSON. This skill produces **only** `status` for each group.

## Key Rules

- **Source of truth:** take every number, name, and gate from that group's own block in `all_groups_report.json`.
- **Single entry point:** run everything through [process_assurance_rag.py](../../scripts/process_assurance_rag.py) with `--stage groups|read|classify|write`. Don't call `write-json.py` yourself.
- **Exit codes:** `0` means success. Any other exit means stop — the script prints an `ERROR:` saying why.
- **Checkpoints:** pass each step's checkpoint before moving on, and **print the checklist in the chat** as you pass it — an unprinted checkpoint is not a guardrail. Tick `[ok]` only for a check you actually ran and that passed. `groups`, `read`, and `classify` are safe; `write` changes the file.
- **Scope:** one field only — `status`. Never write `path_to_green` or any narrative field.
- **Deterministic classification:** `status` is not a free-form judgement call — `--stage classify` computes it from the group's own evidence (missing_config %, Quality Gate failure %, blocker/high/medium issue counts), per the posture rules in the persona. `--stage write` re-derives the same classification at write time and **refuses to write** if `--status` does not match it exactly (exit `2`). Always pass `--stage classify`'s output verbatim to `--stage write`.

## Workflow — per-group loop, repeat for every group in the group list

### Step 0: List the groups — `--stage groups`

```bash
python scripts/process_assurance_rag.py --stage groups \
  --group-map $group_to_project_mapping
```

Output: the list of all group names from `project_group_map.json` (e.g. `IDM`, `SFI`, `Future Grants `, `Trade Plants Portal`, etc.).

**CRITICAL:** use each group name EXACTLY as returned — do not add quotes, apostrophes, or otherwise modify the string. Reuse the exact string in every later step for that group.

**Checkpoint:**

- [ ] persona file read this conversation
- [ ] exit `0`
- [ ] full group list captured

---

### Step 1: Read the group's evidence — `--stage read`

```bash
python scripts/process_assurance_rag.py --stage read \
  --report-file $all_group_report_file --group "$group_name"
```

Output: the full JSON block for that group from `all_groups_report.json` (`quality_gate`, `code_quality`, `severity_breakdown`, `governance.missing_config`, etc.). This is the only evidence you may use for Step 2.

**Checkpoint:**

- [ ] exit `0`
- [ ] group's `quality_gate`, `severity_breakdown`, and `governance.missing_config` identified

---

### Step 2: Calculate the RAG status — `--stage classify`

```bash
python scripts/process_assurance_rag.py --stage classify \
  --report-file $all_group_report_file --group "$group_name"
```

This deterministically computes `status` from the Step 1 evidence, per the posture classification rules in the persona — it is not a free-form judgement call. It also prints the supporting arithmetic (`missing_config_pct`, `qg_fail_pct`, `has_blocker_or_high`, `has_medium`) for audit. Use the printed `status` verbatim in Step 3.

**Checkpoint:**

- [ ] exit `0`
- [ ] `status` is one of `Green`/`Amber`/`Red` as printed by `--stage classify` — not a value you calculated by hand

---

### Step 3: Write the group's result — `--stage write`

**MUTATING.**

```bash
python scripts/process_assurance_rag.py --stage write \
  --report-file $all_group_report_file --group "$group_name" \
  --status "$status"
```

If `--status` does not match what `--stage classify` computes for this group at write time, the script exits `2` with an `ERROR:` and writes nothing — this is expected behaviour if the underlying evidence changed between Step 2 and Step 3, not a bug to work around. Re-run Step 2 and retry with the freshly computed value.

**Checkpoint:**

- [ ] exit `0` with `Written -> <path>`
- [ ] re-run Step 1 for the same group and confirm `status` matches what was written
- [ ] repeat Steps 1–3 for every remaining group in the Step 0 list
