# Examples — Repository Maintenance

This file contains a full illustrative example of the `narrative` plus every section's `_insights` and `_action` values. These values are illustrative only — always derive real outputs from `data-files/sonar_repo_metrics.json` and the templates.

```
narrative: "The technical fundamentals are in good shape. Quality Gate assignments are largely consistent and rule profiles are consistently applied across both organisations. The bigger concern is process discipline. Lifecycle management, configuration hygiene, and auditability are inconsistent, pointing to teams that set Sonar up and then step back. Two decisions would have the most impact: rationalise inactive projects and fix configuration gaps, then enforce a standard Quality Gate and require justification comments on every accepted issue. Acting on these areas will close the most significant governance gaps across the portfolio."

inactive_repositories_by_age_insights: "Removing unused repositories can help to reduce unnecessary cost and maintenance effort. 56 repositories are stale and have not been scanned for more than one year. This includes 10 repositories inactive for 1–2 years, 19 inactive for 2–4 years, and 27 inactive for more than four years."
inactive_repositories_by_age_action:   "Request project POCs to review these repositories for continued relevance, with inactive ones to be removed or archived from the SonarScan instance to optimise cost and maintain a clear project portfolio."

high_duplication_repositories_insights: "10 repositories exceed the duplication threshold (>15%) for overall code. The Quality Gate controls duplication on new code (≤3%) but does not enforce it on overall code. This leads to increased lines of code (LOC)—raising SonarCloud costs (as pricing is LOC-based)—and higher compute, storage, and analysis overhead in self-hosted SonarQube, alongside elevated maintenance effort."
high_duplication_repositories_action:   "Review the identified repositories with respective project POCs to reduce duplication, optimise code efficiency, and improve overall maintainability."

repos_non_standard_main_branch_insights: "72 repositories are set up in Sonar to scan a branch other than the expected main branch. This can lead to confusion and make reports less consistent across projects."
repos_non_standard_main_branch_action:   "Review these repositories with project POCs to confirm the correct branch is set for scanning, and update it where needed for consistency."

repos_with_inactive_non_main_branches_insights: "Five repositories have non-main branches (e.g. feature or development branches) that have not been scanned for more than 180 days, which may indicate stale or abandoned work."
repos_with_inactive_non_main_branches_action:   "Review these repositories with project POCs to confirm if they are still needed, and remove or clean them up to maintain a well-managed Sonar environment."

repos_with_excess_non_main_branches_insights: "Four repositories have more non-main branches than the agreed threshold, which can clutter scan results and make reporting harder to follow."
repos_with_excess_non_main_branches_action:   "Review these repositories with project POCs to consolidate or remove surplus non-main branches and keep the branch count within the agreed threshold."

accepted_issues_insights: "Six repositories have accepted issues without justification comments, weakening auditability and making it difficult to understand why issues were suppressed."
accepted_issues_action:   "Add justification comments to all accepted issues in the affected repositories so suppression decisions remain auditable."

false_positive_counts_insights: "Five repositories contain false positives, with one lacking a justification comment, limiting traceability and auditability."
false_positive_counts_action:   "Review false-positive markings to confirm they are valid and consistently applied, and add justification comments where missing."

non_compliant_quality_gates_insights: "Five repositories are using a non-default Defra Quality Gate, leading to inconsistent evaluation of code quality conditions across the portfolio."
non_compliant_quality_gates_action:   "Reassign the affected repositories to the default Defra Quality Gate to ensure consistent measurement against standard conditions, or review and confirm the justification for using a non-compliant Quality Gate with stakeholders/assurance team."

repos_with_configuration_issues_insights: "59 repositories lack valid configuration, preventing analysis and metric computation."
repos_with_configuration_issues_action:   "Fix configuration in the affected repositories to restore analysis and metric computation."

private_repositories_migration_candidates_insights: "154 private repositories are present in the portfolio. In SonarCloud, analysis of private repositories is billed based on total lines of code (LOC), meaning a higher number of private repositories directly increases subscription cost, unlike public repositories which can be analysed without cost under open-source plans. This may lead to avoidable spending if some repositories can be made public or consolidated. Additionally, retaining all repositories on SonarCloud may not be optimal for large portfolios, where self-hosted SonarQube could offer more cost control depending on infrastructure strategy."
private_repositories_migration_candidates_action:   "Review the 154 private repositories with respective project POCs to validate visibility requirements (public vs private) and assess opportunities to optimise cost by making eligible repositories public or evaluating migration to self-hosted SonarQube where appropriate."

naming_oddities_insights: "Repositories are not following consistent naming conventions. This can make it difficult to identify, manage, and report on projects across the portfolio."
naming_oddities_action:   "Review repository naming with project POCs to ensure alignment with the defined standards, and update names where needed for consistency and clarity."

sonarcloud_rule_analysis_insights: "All repositories are using the correct quality profile rules, ensuring consistent code quality checks."
sonarcloud_rule_analysis_action:   "No action needed; all repositories are compliant with the defined quality profile rules."

```
