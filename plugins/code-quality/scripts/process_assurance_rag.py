#!/usr/bin/env python
"""process_assurance_rag.py — single entry point for the code-assurance-rag skill.

Wraps the per-group RAG workflow behind one command so the skill file lists one
call per step instead of ad-hoc inline `python3 -c` commands:

  --stage groups   -> lists every group name from project_group_map.json (READ-ONLY)
  --stage read     -> prints the full JSON block for one group from
                      all_groups_report.json (READ-ONLY)
  --stage classify -> deterministically computes `status` for one group from
                      its own evidence, per the persona's posture rules (READ-ONLY)
  --stage write    -> writes only `status` for one group back into
                      all_groups_report.json; refuses to write if --status
                      does not match --stage classify's own result (MUTATING)

This skill produces exactly one field per group — `status` (the RAG value) —
nothing else.

Exit codes:
    0  success
    1  input file missing, unreadable, or not valid JSON
    2  group name not found in the file, or --status is not Green/Amber/Red,
       or (write) --status does not match the deterministic classification
    3  wrapper-level argument error (e.g. missing required option)

Usage:
    python process_assurance_rag.py --stage groups --group-map data-files/project_group_map.json
    python process_assurance_rag.py --stage read  --report-file data-files/all_groups_report.json --group IDM
    python process_assurance_rag.py --stage classify --report-file data-files/all_groups_report.json --group IDM
    python process_assurance_rag.py --stage write --report-file data-files/all_groups_report.json --group IDM \\
        --status Amber
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

VALID_STATUSES = ("Green", "Amber", "Red")


def _load(path: Path) -> dict:
    """Load a JSON file with explicit UTF-8; exit 1 on any failure."""
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    try:
        # encoding='utf-8' is required on Windows: open() defaults to cp1252
        # and fails on UTF-8 characters such as smart quotes.
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read file '{path}': {exc}", file=sys.stderr)
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


def _stage_groups(group_map: str) -> int:
    data = _load(Path(group_map))
    if not isinstance(data, dict) or not data:
        print("ERROR: group map must be a non-empty JSON object", file=sys.stderr)
        return 2
    for name in data.keys():
        print(name)
    return 0


def _stage_read(report_file: str, group: str) -> int:
    data = _load(Path(report_file))
    if group not in data:
        print(f"ERROR: group '{group}' not found in {report_file}", file=sys.stderr)
        return 2
    print(json.dumps(data[group], indent=2, ensure_ascii=False))
    return 0


def _pct(part: float, whole: float) -> float:
    """Return part/whole as a percentage, rounded to 1 dp (0 if whole is 0)."""
    if whole <= 0:
        return 0.0
    return round(part / whole * 100.0, 1)


def _classify(group_data: dict) -> dict:
    """Deterministically compute `status` from a group's own evidence.

    Implements the posture classification rules in
    skills/code-assurance-rag/persona/code-assurance-rag.md:

      Green  - all QGs pass, no blocker/high/medium issues, missing_config <=25%
      Amber  - no blocker/high but medium present, OR QG failures <=25%,
               OR missing_config >25% and <100%
      Red    - QG failures >25%, OR blocker/high issues present,
               OR missing_config = 100%
    """
    total_projects = _num(group_data.get("total_projects"))
    missing_config = group_data.get("governance", {}).get("missing_config") or []
    missing_config_pct = _pct(len(missing_config), total_projects)

    qg = group_data.get("quality_gate", {}) or {}
    qg_failed = _num(qg.get("failed"))
    qg_fail_pct = _pct(qg_failed, total_projects)

    severity = group_data.get("severity_breakdown", {}) or {}
    has_blocker_or_high = any(
        _num(bucket.get("blocker")) > 0 or _num(bucket.get("high")) > 0
        for bucket in severity.values()
        if isinstance(bucket, dict)
    )
    has_medium = any(
        _num(bucket.get("medium")) > 0
        for bucket in severity.values()
        if isinstance(bucket, dict)
    )

    if qg_fail_pct > 25 or has_blocker_or_high or missing_config_pct == 100:
        status = "Red"
    elif has_medium or (qg_failed > 0 and qg_fail_pct <= 25) or (25 < missing_config_pct < 100):
        status = "Amber"
    else:
        status = "Green"

    return {
        "status": status,
        "missing_config_pct": missing_config_pct,
        "qg_fail_pct": qg_fail_pct,
        "has_blocker_or_high": has_blocker_or_high,
        "has_medium": has_medium,
    }


def _num(value) -> float:
    """Coerce a value to float; None / blank / non-numeric become 0.0."""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _stage_classify(report_file: str, group: str) -> int:
    data = _load(Path(report_file))
    if group not in data:
        print(f"ERROR: group '{group}' not found in {report_file}", file=sys.stderr)
        return 2

    result = _classify(data[group])
    print("missing_config_pct:", result["missing_config_pct"])
    print("qg_fail_pct:", result["qg_fail_pct"])
    print("has_blocker_or_high:", result["has_blocker_or_high"])
    print("has_medium:", result["has_medium"])
    print("status:", result["status"])
    return 0


def _stage_write(report_file: str, group: str, status: str) -> int:
    if status not in VALID_STATUSES:
        print(f"ERROR: --status must be one of {VALID_STATUSES}, got: {status!r}", file=sys.stderr)
        return 2
    report_path = Path(report_file)
    data = _load(report_path)
    if group not in data:
        print(f"ERROR: group '{group}' not found in {report_file}", file=sys.stderr)
        return 2

    expected = _classify(data[group])["status"]
    if status != expected:
        print(
            f"ERROR: --status '{status}' does not match the deterministic "
            f"classification '{expected}' for group '{group}'. Re-run "
            f"--stage classify and use its output verbatim.",
            file=sys.stderr,
        )
        return 2

    data[group]["status"] = status
    _atomic_write(data, report_path)
    # Plain ASCII: Windows consoles default to cp1252, which can't encode "->" as an arrow glyph.
    print(f"Written -> {report_file}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Single entry point for code-assurance-rag.")
    ap.add_argument("--stage", required=True, choices=("groups", "read", "classify", "write"))
    ap.add_argument("--group-map", help="[groups] Path to project_group_map.json.")
    ap.add_argument("--report-file", help="[read/classify/write] Path to all_groups_report.json.")
    ap.add_argument("--group", help="[read/classify/write] Exact group name.")
    ap.add_argument("--status", help="[write] Green | Amber | Red.")
    args = ap.parse_args()

    if args.stage == "groups":
        if not args.group_map:
            print("ERROR: --stage groups requires --group-map", file=sys.stderr)
            return 3
        return _stage_groups(args.group_map)

    if not args.report_file or not args.group:
        print(f"ERROR: --stage {args.stage} requires --report-file and --group", file=sys.stderr)
        return 3

    if args.stage == "read":
        return _stage_read(args.report_file, args.group)

    if args.stage == "classify":
        return _stage_classify(args.report_file, args.group)

    if args.status is None:
        print("ERROR: --stage write requires --status", file=sys.stderr)
        return 3
    return _stage_write(args.report_file, args.group, args.status)


if __name__ == "__main__":
    raise SystemExit(main())
