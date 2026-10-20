---
name: code-repo-maintenance-check
description: Monitor CCTS repository health using Sonar metrics, including LOC, repository inactivity, code duplication, branch hygiene, quality profile compliance, and auditability. Identify threshold breaches and generate the report.
---

# Code Repo Maintenance Check

**Before anything else:** open and read the file [code-repo-maintenance-check.md](persona/code-repo-maintenance-check.md) in full. Its role, context, and constraints apply to every step in this file — do not start the workflow below without reading it.

Runbook: read `$sonar_repo_metrics_file` → compute cost intelligence → generate insights/actions → write back to the same file.

## Key Rules

- **File:** `$sonar_repo_metrics_file` — read in Step 0, updated in Step 1, written in Step 3. Same file in, same file out. Never touch `all_groups_report.json` or `project_group_map.json` (that's `code-assurance-rag`).
- **Source of truth:** take every number, name, and gate from `$sonar_repo_metrics_file`
- **Single entry point:** run everything through [process_sonar_metrics.py](../../scripts/process_sonar_metrics.py) with `--stage read|cost|write`. Don't call the underlying scripts yourself.
- **Exit codes:** `0` means success. Any other exit means stop — the script prints an `ERROR:` saying why.
- **Checkpoints:** pass each step's checkpoint before moving on, and **print the checklist in the chat** as you pass it — an unprinted checkpoint is not a guardrail. Tick `[ok]` only for a check you actually ran and that passed. `read` is safe; `cost` and `write` change the file.

## Workflow
### Step 0: Read the evidence — `--stage read`

```bash
python scripts/process_sonar_metrics.py --stage read \
  --governance-file $sonar_repo_metrics_file
```

This prints the platform, repository totals, the section counts, and the full `odd_names` list.

Each field name below becomes `<base>_insights`/`<base>_action` after analysis as per persona and written back to `$sonar_repo_metrics_file` in Step 3:

| Field base name | Applies to | Evidence type | Where to read it |
| --------------- | ---------- | -------------- | ----------------- |
| `inactive_repositories_by_age` | Both | Count | `consolidated_metrics.inactive_repositories_by_age.<single value>` |
| `high_duplication_repositories` | Both | Count | `consolidated_metrics.high_duplication_repositories.repos_over_threshold` |
| `private_repositories_migration_candidates` | SonarCloud only | Count | `consolidated_metrics.private_repositories_migration_candidates.<single value>` |
| `false_positive_counts` | Both | Count | `consolidated_metrics.false_positive_counts.<single value>` |
| `accepted_issues` | Both | Count | `consolidated_metrics.accepted_issues.<single value>` |
| `non_compliant_quality_gates` | Both | Count | `consolidated_metrics.non_compliant_quality_gates.<single value>` |
| `repos_with_configuration_issues` | Both | Count | `consolidated_metrics.repos_with_configuration_issues.<single value>` |
| `repos_non_standard_main_branch` | Both | Count | `consolidated_metrics.branch_hygiene.repos_non_standard_main_branch` |
| `repos_with_inactive_non_main_branches` | Both | Count | `consolidated_metrics.branch_hygiene.repos_with_inactive_non_main_branches` |
| `repos_with_excess_non_main_branches` | Both | Count | `consolidated_metrics.branch_hygiene.repos_with_excess_non_main_branches` |
| `naming_oddities` | Both | Full list | `sections.odd_names` (no count) |
| `sonarqube_rule_analysis` | SonarQube only | Full list | `sonar_rules_analysis` |
| `sonarcloud_rule_analysis` | SonarCloud only | Full list | `sonar_rules_analysis_defra` + `sonar_rules_analysis_defragovuk` |

**Checkpoint:** 
- [ ] persona file read this conversation
- [ ] exit `0`
- [ ] `platform` is `sonarqube` or `sonarcloud`
- [ ] `total_repos` is numeric
- [ ] at least three `consolidated_metrics` counts identified.

---

### Step 1: Cost intelligence & narrative — `--stage cost`

**MUTATING.**

```bash
python scripts/process_sonar_metrics.py --stage cost \
  --governance-file $sonar_repo_metrics_file
```

**Checkpoint:** 
- [ ] exit `0` (no `ERROR:`) ·
- [ ] `cost_intelligence_narrative` captured verbatim.

---

### Step 2: Author the insights

Write the `ai_insights` values, following the persona's wording rules. Produce a `narrative` plus a `<base>_insights` and `<base>_action` field for **every** section base name in the Step 0 table — all **plain text**:

1. **narrative** (required) — a single plain-text portfolio overview paragraph (platform, total repositories, most material findings), immediately followed by the verbatim `cost_intelligence_narrative` from Step 1.
2. **`<base>_insights`** (required for every row in the Step 0 table) — the evidence-led observation, tied to real counts.
3. **`<base>_action`** (required for every row in the Step 0 table) — the specific, actionable remediation for that observation.
4. Leave a base name's `_insights`/`_action` pair as `""`/`""` **only** when Step 0 found no evidence for it (e.g. `sonarqube_rule_analysis` on a SonarCloud platform) — never leave a row empty just because it wasn't gotten to.

A full worked example of every field is in [EXAMPLES.md](EXAMPLES.md).

Then:
1. Copy the template for your platform.
2. Fill in each value as plain text; leave `""` only per rule 4 above.
3. Save it as e.g. `data-files/sonar_repo_metrics_values.json`.

Templates: [SonarCloud](templates/values.sonarcloud.template.json) · [SonarQube](templates/values.sonarqube.template.json)

**Checkpoint:**
- [ ] every row in the Step 0 table has a corresponding `<base>_insights`/`<base>_action` pair in the values file
- [ ] each populated pair is filled with real, evidence-led text (not left as the template's `""` placeholder) — list any row still `""` and confirm it is a genuine no-evidence case, not an oversight
- [ ] `narrative` ends with the verbatim Step 1 cost narrative

---

### Step 3: Write the insights — `--stage write`

**MUTATING.**

```bash
python scripts/process_sonar_metrics.py --stage write \
  --governance-file $sonar_repo_metrics_file \
  --values-file data-files/sonar_repo_metrics_values.json
```

**Checkpoint:** 
- [ ] exit `0` with `Written -> <path>`
- [ ] values file uses the chosen platform template's keys
- [ ] re-run Step 0 (`--stage read`) or open `$sonar_repo_metrics_file` and confirm `ai_insights.sections` now contains every row from the Step 0 table with the same non-empty content authored in Step 2 — not just `narrative` alone