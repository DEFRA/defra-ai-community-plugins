#!/usr/bin/env python
"""process_sonar_metrics.py — single entry point for the code-repo-maintenance-check skill.

Everything the skill needs lives in this one file (no other scripts are
shelled out to):

  --stage read   -> READ-ONLY: prints platform/repo totals/consolidated_metrics
                    counts/section counts/odd_names from the governance JSON.
  --stage cost   -> MUTATING: computes deterministic Sonar licence cost
                    intelligence (utilisation, headroom, reclaimable LOC) and
                    writes `cost_intelligence` + `cost_intelligence_narrative`
                    back into the governance JSON.
  --stage write  -> MUTATING: writes `ai_insights` values (produced by the
                    agent as a flat JSON *values file*) back into the
                    governance JSON: `narrative` -> `ai_insights.narrative`,
                    every other key -> `ai_insights.sections.<key>`.

Nothing here invents counts, keys, or values — `read` only reflects what is
already in the file, `cost` is pure arithmetic over measured LOC figures, and
`write` only stores exactly what the caller supplies.

Exit codes:
    0  success
    1  governance file missing, unreadable, or not valid JSON
    2  `platform_filter` missing/invalid (read), or unknown platform (cost)
    3  wrapper-level argument/input error (e.g. missing or invalid values file)

Usage:
    python process_sonar_metrics.py --stage read  --governance-file data-files/sonar_repo_metrics.json
    python process_sonar_metrics.py --stage cost  --governance-file data-files/sonar_repo_metrics.json
    python process_sonar_metrics.py --stage write --governance-file data-files/sonar_repo_metrics.json --values-file values.json
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

VALID_PLATFORMS = ("sonarqube", "sonarcloud")


# ---------------------------------------------------------------------------
# Shared I/O helpers
# ---------------------------------------------------------------------------
def _load(gov_path: Path) -> dict:
    """Load the governance JSON with explicit UTF-8; exit 1 on any failure."""
    if not gov_path.exists():
        print(f"ERROR: governance file not found: {gov_path}")
        raise SystemExit(1)
    try:
        # encoding='utf-8' is required on Windows: open() defaults to cp1252
        # and fails on UTF-8 characters such as smart quotes.
        with open(gov_path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read governance file '{gov_path}': {exc}")
        raise SystemExit(1)


def _atomic_write(data: dict, output_path: Path) -> None:
    """Write *data* as pretty-printed JSON atomically (temp file + os.replace)."""
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=output_path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp_path, output_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# --stage read
# ---------------------------------------------------------------------------
def _stage_read(gov_file: str) -> int:
    data = _load(Path(gov_file))

    platform = str(data.get("platform_filter", "")).strip().lower()
    if platform not in VALID_PLATFORMS:
        print(f"ERROR: platform_filter must be one of {VALID_PLATFORMS}, "
              f"got: {data.get('platform_filter')!r}")
        return 2

    print("platform:", platform)
    print("total_repos:", data.get("total_repos"))
    print("consolidated_metrics:",
          json.dumps(data.get("consolidated_metrics"), indent=2, ensure_ascii=False))

    sections = data.get("sections") or {}
    print("section_counts:")
    for key, value in sections.items():
        length = len(value) if isinstance(value, (list, dict)) else type(value).__name__
        print(f"  {key} -> {length}")

    print("odd_names:",
          json.dumps(sections.get("odd_names"), indent=2, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
# --stage cost — deterministic Sonar licence cost intelligence
# ---------------------------------------------------------------------------
def _parse_env(env_path: Path) -> dict[str, str]:
    """Parse a simple KEY=VALUE .env file, ignoring blanks and # comments."""
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip()
    return values


def _env_int(env: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(str(env.get(key, default)).strip())
    except (TypeError, ValueError):
        return default


def _num(value) -> float:
    """Coerce a value to float; None / blank / non-numeric become 0.0."""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _pct(part: float, whole: float) -> float:
    """Return part/whole as a percentage, rounded to 1 dp (0 if whole is 0)."""
    if whole <= 0:
        return 0.0
    return round(part / whole * 100.0, 1)


def _risk_band(util_pct: float, high: float, medium: float) -> str:
    if util_pct >= high:
        return "High"
    if util_pct >= medium:
        return "Medium"
    return "Low"


def _project_metrics(record: dict) -> dict:
    """Extract the deterministic fields needed for cost intelligence."""
    coverage_raw = record.get("COVERAGE_OVERALL")
    return {
        "name": record.get("Name"),
        "organisation": str(record.get("Organisation") or "").strip().lower(),
        "visibility": str(record.get("Repo visibility") or "").strip().lower(),
        "ncloc": _num(record.get("ncloc")),
        "dup_pct": _num(record.get("duplicated_lines_density")),
        "coverage": None if coverage_raw is None else _num(coverage_raw),
        "days_since_scan": _num(record.get("Days Since Last Scan")),
    }


def _summarise(projects: list[dict], inactive_days: float, dup_threshold: float,
               billing_basis: str) -> dict:
    """Compute the deterministic LOC signals for a set of projects.

    ``billing_basis`` is 'private' (SonarCloud) or 'total' (SonarQube) and
    controls which LOC count toward the billed / reclaimable figures.
    """
    def billable(p: dict) -> float:
        if billing_basis == "private":
            return p["ncloc"] if p["visibility"] == "private" else 0.0
        return p["ncloc"]

    # On the 'private' basis, public projects are excluded from billed figures
    # and from the project counts, since they never affect the licence.
    def in_scope(p: dict) -> bool:
        return p["visibility"] == "private" if billing_basis == "private" else True

    total_loc = sum(p["ncloc"] for p in projects)
    private_loc = sum(p["ncloc"] for p in projects if p["visibility"] == "private")
    public_loc = sum(p["ncloc"] for p in projects if p["visibility"] == "public")
    billed_loc = sum(billable(p) for p in projects)

    inactive = [p for p in projects if p["days_since_scan"] > inactive_days]
    active = [p for p in projects if p["days_since_scan"] <= inactive_days]

    inactive_loc = sum(p["ncloc"] for p in inactive)
    inactive_billable_loc = sum(billable(p) for p in inactive)

    # Duplicated LOC in projects that are still active (avoid double counting the
    # inactive projects already fully reclaimable above).
    active_dup_billable_loc = sum(
        round(billable(p) * p["dup_pct"] / 100.0)
        for p in active if p["dup_pct"] > dup_threshold
    )

    reclaimable_billable_loc = round(inactive_billable_loc + active_dup_billable_loc)

    # Potential test/source identification issue: active projects carrying code
    # (ncloc > 0) with a *measured* 0% coverage. Missing coverage is not flagged,
    # to avoid sweeping in every project (and public, unbilled code).
    no_cov = [p for p in active if p["ncloc"] > 0 and p["coverage"] == 0.0]
    no_cov_billable_loc = sum(billable(p) for p in no_cov)

    return {
        "total_loc": int(round(total_loc)),
        "private_loc": int(round(private_loc)),
        "public_loc": int(round(public_loc)),
        "billing_basis": billing_basis,
        "public_loc_excluded": billing_basis == "private",
        "billed_loc": int(round(billed_loc)),
        "inactive_projects": sum(1 for p in inactive if in_scope(p)),
        "inactive_loc": int(round(inactive_loc)),
        "inactive_billable_loc": int(round(inactive_billable_loc)),
        "high_duplication_projects": sum(1 for p in active if p["dup_pct"] > dup_threshold and in_scope(p)),
        "active_duplicated_billable_loc": int(active_dup_billable_loc),
        "reclaimable_billable_loc": int(reclaimable_billable_loc),
        "no_coverage_projects": sum(1 for p in no_cov if in_scope(p)),
        "no_coverage_billable_loc": int(round(no_cov_billable_loc)),
    }


def _fmt(n: int) -> str:
    return f"{n:,}"


def _org_basis(env: dict, org_key: str) -> str:
    """Billing basis for a SonarCloud org from .env; 'private' excludes public LOC."""
    raw = str(env.get(f"SONARCLOUD_{org_key.upper()}_BILLING_BASIS", "private")).strip().lower()
    return "total" if raw == "total" else "private"


def _s_from_org_breakdown(org: dict, basis: str = "private") -> dict:
    # Explicit public-lines check: on the 'private' basis (SonarCloud default)
    # public LOC is excluded from every billed/billable figure.
    private_only = basis != "total"
    billed = int(org.get("private_loc", 0)) if private_only else int(org.get("total_loc", 0))
    inactive_bill = int(org.get("inactive_private_loc", 0)) if private_only else int(org.get("inactive_loc", 0))
    dup_bill = int(org.get("duplicated_active_private_loc", 0))
    nocov_bill = int(org.get("no_coverage_active_private_loc", 0))
    return {
        "total_loc": int(org.get("total_loc", 0)),
        "private_loc": int(org.get("private_loc", 0)),
        "public_loc": int(org.get("public_loc", 0)),
        "billing_basis": basis,
        "public_loc_excluded": private_only,
        "billed_loc": billed,
        "inactive_projects": int(org.get("inactive_projects", 0)),
        "inactive_loc": int(org.get("inactive_loc", 0)),
        "inactive_billable_loc": inactive_bill,
        "high_duplication_projects": int(org.get("duplicated_projects", 0)),
        "active_duplicated_billable_loc": dup_bill,
        "reclaimable_billable_loc": inactive_bill + dup_bill,
        "no_coverage_projects": int(org.get("no_coverage_projects", 0)),
        "no_coverage_billable_loc": nocov_bill,
    }


def _s_from_total_breakdown(bd: dict) -> dict:
    inactive_bill = int(bd.get("inactive_loc", 0))
    dup_bill = int(bd.get("duplicated_active_loc", 0))
    return {
        "total_loc": int(bd.get("total_loc", 0)),
        "private_loc": int(bd.get("private_loc", 0)),
        "public_loc": int(bd.get("public_loc", 0)),
        "billed_loc": int(bd.get("total_loc", 0)),
        "inactive_projects": int(bd.get("inactive_projects", 0)),
        "inactive_loc": int(bd.get("inactive_loc", 0)),
        "inactive_billable_loc": inactive_bill,
        "high_duplication_projects": int(bd.get("duplicated_projects", 0)),
        "active_duplicated_billable_loc": dup_bill,
        "reclaimable_billable_loc": inactive_bill + dup_bill,
        "no_coverage_projects": int(bd.get("no_coverage_projects", 0)),
        "no_coverage_billable_loc": int(bd.get("no_coverage_active_loc", 0)),
    }


def _build_sonarcloud(org_summaries: dict, env: dict, source: str) -> tuple[dict, str]:
    """Apply licence capacities to per-organisation summaries and compose narrative."""
    high = float(_env_int(env, "LOC_UTILISATION_HIGH_PCT", 90))
    medium = float(_env_int(env, "LOC_UTILISATION_MEDIUM_PCT", 75))

    orgs = {
        "defra": {
            "plan": env.get("SONARCLOUD_DEFRA_PLAN", "Enterprise Edition"),
            "capacity": _env_int(env, "SONARCLOUD_DEFRA_LOC_CAPACITY", 1_000_000),
            "freq": env.get("SONARCLOUD_DEFRA_BILLING_FREQUENCY", ""),
        },
        "defragovuk": {
            "plan": env.get("SONARCLOUD_DEFRAGOVUK_PLAN", "Team plan"),
            "capacity": _env_int(env, "SONARCLOUD_DEFRAGOVUK_LOC_CAPACITY", 300_000),
            "freq": env.get("SONARCLOUD_DEFRAGOVUK_BILLING_FREQUENCY", ""),
        },
    }

    result: dict = {"platform": "sonarcloud", "billing_basis": "private",
                    "source": source, "organisations": {}}
    usage_bits: list[str] = []
    total_reclaim = 0
    total_billed = 0
    for org_key, cfg in orgs.items():
        s = dict(org_summaries.get(org_key, {}))
        util = _pct(s.get("billed_loc", 0), cfg["capacity"])
        s.update({
            "plan": cfg["plan"],
            "loc_capacity": cfg["capacity"],
            "billing_frequency": cfg["freq"],
            "utilisation_pct": util,
            "headroom_loc": cfg["capacity"] - s.get("billed_loc", 0),
            "capacity_risk": _risk_band(util, high, medium),
        })
        result["organisations"][org_key] = s
        total_reclaim += int(s.get("reclaimable_billable_loc", 0))
        total_billed += int(s.get("billed_loc", 0))
        plan_short = cfg["plan"].split()[0] if cfg["plan"] else cfg["plan"]
        usage_bits.append(
            f"{org_key} is using {util}% of its {_fmt(cfg['capacity'])}-line {plan_short} allowance"
        )

    # Cost-saving focused narrative (kept in step with the report's cost card).
    narrative = (
        "Only private lines of code count towards Sonar licence limits; public code "
        "is analysed free of charge. " + ", while ".join(usage_bits) + "."
    )
    if total_reclaim > 0:
        pct_used = _pct(total_reclaim, total_billed)
        across = " across all organisations combined" if len(result["organisations"]) > 1 else ""
        narrative += (
            f" By removing inactive and duplicate projects, up to {_fmt(total_reclaim)} "
            f"private lines, approximately {pct_used}% of the total private lines used"
            f"{across}, could be reclaimed. This would create more licence capacity and "
            f"reduce the need for additional licence spending."
        )
    return result, narrative


def _build_sonarqube(summary: dict, env: dict, source: str) -> tuple[dict, str]:
    high = float(_env_int(env, "LOC_UTILISATION_HIGH_PCT", 90))
    medium = float(_env_int(env, "LOC_UTILISATION_MEDIUM_PCT", 75))
    plan = env.get("SONARQUBE_PLAN", "Enterprise Edition")
    capacity = _env_int(env, "SONARQUBE_LOC_CAPACITY", 5_000_000)
    expiration = env.get("SONARQUBE_EXPIRATION", "")

    s = dict(summary)
    util = _pct(s.get("billed_loc", 0), capacity)
    headroom = capacity - s.get("billed_loc", 0)
    band = _risk_band(util, high, medium)
    s.update({
        "plan": plan,
        "loc_capacity": capacity,
        "expiration": expiration,
        "utilisation_pct": util,
        "headroom_loc": headroom,
        "capacity_risk": band,
    })
    result = {"platform": "sonarqube", "billing_basis": "total",
              "source": source, "instance": s}

    # Cost-saving focused narrative (kept in step with the report's cost card).
    plan_short = plan.split()[0] if plan else plan
    narrative = (
        f"The SonarQube {plan_short} instance is using {util}% of its "
        f"{_fmt(capacity)}-line allowance"
        + (f", which expires on {expiration}" if expiration else "")
        + "."
    )
    if s.get("reclaimable_billable_loc", 0) > 0:
        pct_used = _pct(int(s.get("reclaimable_billable_loc", 0)), int(s.get("billed_loc", 0)))
        narrative += (
            f" By removing inactive and duplicate projects, up to "
            f"{_fmt(int(s['reclaimable_billable_loc']))} lines, approximately {pct_used}% "
            f"of the currently analysed lines, could be reclaimed. This would create more "
            f"licence capacity and reduce the need for additional licence spending."
        )
    return result, narrative


def _stage_cost(gov_file: str) -> int:
    gov_path = Path(gov_file)
    if not gov_path.exists():
        print(f"ERROR: governance file not found: {gov_path}")
        return 1

    # The aging JSON is only a fallback when the governance report lacks a
    # complete loc_breakdown; it is not required.
    aging_path = gov_path.parent / "sonar_aging_merged.json"

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    env = _parse_env(repo_root / ".env")

    thr_path = script_dir.parent / "config" / "governance_thresholds.json"
    inactive_days = 365.0
    dup_threshold = 15.0
    if thr_path.exists():
        thr = json.loads(thr_path.read_text(encoding="utf-8"))
        inactive_days = float(thr.get("inactive_months_threshold", 12)) * 365.0 / 12.0
        dup_threshold = float(thr.get("high_duplication_threshold_pct", 15))

    gov = json.loads(gov_path.read_text(encoding="utf-8"))
    platform = str(gov.get("platform_filter", "")).strip().lower()

    # Prefer the authoritative loc_breakdown (computed from the full portfolio
    # dataframe — the same source as the HTML Sonar Stats). Fall back to the
    # merged aging JSON only when the breakdown is absent or empty.
    bd = gov.get("loc_breakdown") or {}
    breakdown_ok = int(bd.get("total_loc", 0)) > 0
    by_org = bd.get("by_organisation") or {}

    def _aging_summaries():
        if not aging_path.exists():
            print(f"ERROR: loc_breakdown missing and aging file not found: {aging_path}")
            return None
        aging = json.loads(aging_path.read_text(encoding="utf-8"))
        return [_project_metrics(r) for r in aging]

    if platform == "sonarcloud":
        if breakdown_ok and by_org:
            source = "loc_breakdown"
            org_summaries = {k: _s_from_org_breakdown(v, _org_basis(env, k)) for k, v in by_org.items()}
        else:
            projects = _aging_summaries()
            if projects is None:
                return 1
            source = "aging_merged"
            org_summaries = {
                org_key: _summarise([p for p in projects if p["organisation"] == org_key],
                                    inactive_days, dup_threshold, _org_basis(env, org_key))
                for org_key in ("defra", "defragovuk")
            }
        cost, narrative = _build_sonarcloud(org_summaries, env, source)
    elif platform == "sonarqube":
        if breakdown_ok:
            source = "loc_breakdown"
            summary = _s_from_total_breakdown(bd)
        else:
            projects = _aging_summaries()
            if projects is None:
                return 1
            source = "aging_merged"
            summary = _summarise(projects, inactive_days, dup_threshold, "total")
        cost, narrative = _build_sonarqube(summary, env, source)
    else:
        print(f"ERROR: unknown platform_filter '{platform}' in governance file.")
        return 2

    cost["thresholds"] = {
        "inactive_days": int(inactive_days),
        "duplication_pct": dup_threshold,
        "utilisation_high_pct": _env_int(env, "LOC_UTILISATION_HIGH_PCT", 90),
        "utilisation_medium_pct": _env_int(env, "LOC_UTILISATION_MEDIUM_PCT", 75),
    }

    gov["cost_intelligence"] = cost
    gov["cost_intelligence_narrative"] = narrative
    _atomic_write(gov, gov_path)

    print("Cost intelligence written ->", gov_path)
    print("----- COST_INTELLIGENCE_NARRATIVE -----")
    print(narrative)
    print("----- END -----")
    return 0


# ---------------------------------------------------------------------------
# --stage write
# ---------------------------------------------------------------------------
def _stage_write(gov_file: str, values_file: str | None) -> int:
    if not values_file:
        print("ERROR: --stage write requires --values-file")
        return 3
    values_path = Path(values_file)
    if not values_path.exists():
        print(f"ERROR: values file not found: {values_path}")
        return 3
    try:
        # utf-8-sig tolerates an optional BOM that some editors/tools prepend.
        with open(values_path, encoding="utf-8-sig") as fh:
            values = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read values file '{values_path}': {exc}")
        return 3
    if not isinstance(values, dict) or not values:
        print("ERROR: values file must be a non-empty JSON object")
        return 3

    gov_path = Path(gov_file)
    gov = _load(gov_path)
    # Rebuild ai_insights from scratch each run so stale keys/sections left
    # over from a previous run (or a governance file copied from another
    # repo) never survive alongside the newly authored values.
    sections = {key: val for key, val in values.items() if key != "narrative"}
    gov["ai_insights"] = {
        "narrative": values.get("narrative", ""),
        "sections": sections,
    }

    _atomic_write(gov, gov_path)
    # Plain ASCII: Windows consoles default to cp1252, which can't encode "->" as an arrow glyph.
    print(f"Written -> {gov_file}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Single entry point for code-repo-maintenance-check.")
    ap.add_argument("--stage", required=True, choices=("read", "cost", "write"))
    ap.add_argument("--governance-file", required=True,
                    help="Path to sonar_repo_metrics.json.")
    ap.add_argument("--values-file", default=None,
                    help="[write] Flat JSON object of ai_insights values.")
    args = ap.parse_args()

    if args.stage == "read":
        return _stage_read(args.governance_file)
    if args.stage == "cost":
        return _stage_cost(args.governance_file)
    return _stage_write(args.governance_file, args.values_file)


if __name__ == "__main__":
    raise SystemExit(main())
