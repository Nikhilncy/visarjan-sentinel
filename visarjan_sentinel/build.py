"""Run the whole pipeline and write the artefacts to outputs/.

    python -m visarjan_sentinel.build

Writes:
    outputs/validation.json   grid counts and warnings
    outputs/ranking.json      the ranked ghats with reasons, coverage and evidence
    outputs/evidence.csv      one row per grid cell with status, limit, report and page
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from .loader import build_grid, load_readings, validate
from .ranking import FORMULA_TEXT, LIMITATIONS, rank_ghats
from .rules import load_limits, status_of
from .sources import COLIFORM_NOTE, CPCB_CSV, OUTPUT_DIR, READINGS_CSV, UNITS_NOTE


def run(readings_csv: Path = READINGS_CSV, cpcb_csv: Path = CPCB_CSV, out_dir: Path = OUTPUT_DIR) -> dict:
    readings = load_readings(readings_csv)
    grid = build_grid(readings)
    report = validate(readings, grid)
    if not report.ok:
        for w in report.warnings:
            print(w, file=sys.stderr)
        raise SystemExit("Validation failed. Nothing written.")
    limits = load_limits(cpcb_csv)
    scores = rank_ghats(grid, limits)

    out_dir.mkdir(parents=True, exist_ok=True)
    validation = {
        "csv_rows": report.csv_rows,
        "grid_cells": report.grid_cells,
        "state_counts": report.state_counts,
        "duplicate_keys": report.duplicate_keys,
        "absent_tables": [{"site": s, "event": e} for s, e in report.absent_tables],
        "warnings": report.warnings,
    }
    (out_dir / "validation.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False))

    ranking = {
        "water_class": limits.water_class,
        "designated_use": limits.designated_use,
        "limits": {p: {"rule": l.describe(), "type": l.limit_type, "low": l.low, "high": l.high, "unit": l.unit}
                   for p, l in limits.limits.items()},
        "untested_class_b_parameters": limits.untested,
        "formula": FORMULA_TEXT,
        "limitations": LIMITATIONS,
        "notes": [UNITS_NOTE, COLIFORM_NOTE],
        "events": [e.label for e in grid.events],
        "ghats": [g.to_dict() for g in scores],
    }
    (out_dir / "ranking.json").write_text(json.dumps(ranking, indent=2, ensure_ascii=False))

    with open(out_dir / "evidence.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["site", "year", "festival", "phase", "parameter", "state", "value", "unit_assumed",
                    "status", "class_b_limit", "value_as_printed", "parameter_as_printed",
                    "site_as_printed", "site_match_confidence", "report_file", "source_page"])
        for r in grid.readings:
            lim = limits.limits.get(r.parameter)
            w.writerow([r.site, r.event.year, r.event.festival, r.phase, r.parameter, r.state,
                        "" if r.value is None else r.value, r.unit, status_of(r, limits),
                        lim.describe() if lim else "", r.value_as_printed, r.parameter_as_printed,
                        r.site_as_printed, r.site_match_confidence, r.report_file,
                        "" if r.source_page is None else r.source_page])
    return {"validation": validation, "ranking": ranking}


if __name__ == "__main__":
    result = run()
    print(f"grid cells: {result['validation']['grid_cells']}  states: {result['validation']['state_counts']}")
    for g in result["ranking"]["ghats"]:
        print(f"{g['rank']}. T{g['tier']} {g['site']:<40} share={g['exceedance_share']:.3f} "
              f"({g['exceedances']}/{g['numeric_scored']}) minDO={g['min_do']} "
              f"coverage={g['coverage']['sampled_share']:.0%}")
