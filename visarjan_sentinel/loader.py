"""Load the Bhopal readings CSV and build the full expected data grid.

Every cell of the grid (site x event x phase x parameter) ends up in exactly one
of four states:

    numeric        a number was printed (0 is a real numeric reading, not missing)
    bdl            printed as BDL / ND: detected below the lab's limit, not zero
    not_sampled    the table exists but the cell is blank, '_', '-', '*' or '**'
    absent_table   the report has no table for this site and event at all

The grid is what makes missing data visible. A ghat with few rows in the CSV
is not "clean"; it is unsampled.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .sources import BHOPAL_GHATS, FESTIVAL_ORDER, PHASES, REPORTS

NUMERIC = "numeric"
BDL = "bdl"
NOT_SAMPLED = "not_sampled"
ABSENT_TABLE = "absent_table"
STATES = (NUMERIC, BDL, NOT_SAMPLED, ABSENT_TABLE)

BDL_FLAGS = {"BDL", "ND"}


@dataclass(frozen=True, order=True)
class Event:
    """One festival in one year. Sorts chronologically."""

    year: int
    festival: str

    @property
    def sort_key(self) -> tuple[int, int]:
        return (self.year, FESTIVAL_ORDER[self.festival])

    @property
    def label(self) -> str:
        return f"{self.festival} {self.year}"


@dataclass(frozen=True)
class Reading:
    """One cell of the grid, with everything needed to trace it to the PDF."""

    event: Event
    site: str
    water_body: str
    phase: str
    parameter: str
    state: str
    value: float | None
    unit: str
    flag: str
    value_as_printed: str
    parameter_as_printed: str
    site_as_printed: str
    site_match_confidence: str
    source_page: int | None

    @property
    def report_file(self) -> str:
        return REPORTS[self.event.year].file_name

    @property
    def report_title(self) -> str:
        return REPORTS[self.event.year].title

    @property
    def citation(self) -> str:
        if self.source_page is None:
            return f"{self.report_title}: no table for this site"
        return f"{self.report_title}, page {self.source_page}"


def _parse_row(row: dict[str, str]) -> Reading:
    raw_value = row["value"].strip()
    flag = row["flag"].strip()
    if raw_value != "":
        state, value = NUMERIC, float(raw_value)
    elif flag in BDL_FLAGS:
        state, value = BDL, None
    else:
        state, value = NOT_SAMPLED, None
    return Reading(
        event=Event(int(row["year"]), row["festival"]),
        site=row["site"],
        water_body=row["water_body"],
        phase=row["phase"],
        parameter=row["parameter"],
        state=state,
        value=value,
        unit=row["unit_assumed"],
        flag=flag,
        value_as_printed=row["value_as_printed"],
        parameter_as_printed=row["parameter_as_printed"],
        site_as_printed=row["site_as_printed"],
        site_match_confidence=row["site_match_confidence"],
        source_page=int(row["source_page"]),
    )


def load_readings(path: Path) -> list[Reading]:
    """Read the CSV as printed. One Reading per CSV row, no grid filling yet."""
    with open(path, newline="", encoding="utf-8") as f:
        return [_parse_row(r) for r in csv.DictReader(f)]


@dataclass
class Grid:
    """All expected cells, including the ones the reports never printed."""

    readings: list[Reading]
    events: list[Event]
    sites: list[str]
    parameters_by_event: dict[Event, list[str]]
    site_info: dict[str, dict[str, str]]  # site -> water_body, confidence

    def for_site(self, site: str) -> list[Reading]:
        return [r for r in self.readings if r.site == site]

    def lookup(self, site: str, event: Event, phase: str, parameter: str) -> Reading | None:
        for r in self.readings:
            if r.site == site and r.event == event and r.phase == phase and r.parameter == parameter:
                return r
        return None

    def expected_cells(self, site: str) -> int:
        return sum(len(self.parameters_by_event[e]) * len(PHASES) for e in self.events)

    def table_present(self, site: str, event: Event) -> bool:
        return any(r.site == site and r.event == event and r.state != ABSENT_TABLE for r in self.readings)


def build_grid(readings: list[Reading]) -> Grid:
    """Fill the expected site x event x phase x parameter grid.

    The parameter list for an event is whatever the reports printed for that
    event at any Bhopal ghat (Suspended solids is only in four of six events).
    A site with no rows for an event gets one absent_table cell per expected
    parameter and phase, so the gap is counted and shown, never ignored.
    """
    events = sorted({r.event for r in readings}, key=lambda e: e.sort_key)
    params_by_event: dict[Event, list[str]] = {}
    for e in events:
        seen: dict[str, None] = {}
        for r in readings:
            if r.event == e:
                seen.setdefault(r.parameter, None)
        params_by_event[e] = list(seen)

    sites = [s for s in BHOPAL_GHATS if any(r.site == s for r in readings)]
    extra = sorted({r.site for r in readings} - set(sites))
    sites += extra  # unknown names are kept, not dropped

    site_info: dict[str, dict[str, str]] = {}
    for r in readings:
        site_info.setdefault(r.site, {"water_body": r.water_body, "confidence": r.site_match_confidence})

    index = {(r.site, r.event, r.phase, r.parameter): r for r in readings}
    filled: list[Reading] = []
    for site in sites:
        for e in events:
            present = any(k[0] == site and k[1] == e for k in index)
            for phase in PHASES:
                for param in params_by_event[e]:
                    r = index.get((site, e, phase, param))
                    if r is not None:
                        filled.append(r)
                        continue
                    unit = next((x.unit for x in readings if x.parameter == param), "")
                    filled.append(
                        Reading(
                            event=e,
                            site=site,
                            water_body=site_info[site]["water_body"],
                            phase=phase,
                            parameter=param,
                            state=ABSENT_TABLE if not present else NOT_SAMPLED,
                            value=None,
                            unit=unit,
                            flag="absent table" if not present else "row missing from parsed table",
                            value_as_printed="",
                            parameter_as_printed="",
                            site_as_printed="",
                            site_match_confidence=site_info[site]["confidence"],
                            source_page=None,
                        )
                    )
    return Grid(filled, events, sites, params_by_event, site_info)


@dataclass
class ValidationReport:
    csv_rows: int
    grid_cells: int
    state_counts: dict[str, int]
    duplicate_keys: int
    absent_tables: list[tuple[str, str]]  # (site, event label)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.duplicate_keys == 0 and not any(w.startswith("ERROR") for w in self.warnings)


def validate(readings: list[Reading], grid: Grid) -> ValidationReport:
    """Sanity checks that must hold before any ranking is trusted."""
    keys = Counter((r.site, r.event, r.phase, r.parameter) for r in readings)
    dupes = sum(1 for v in keys.values() if v > 1)
    states = Counter(r.state for r in grid.readings)
    absent = sorted(
        {(r.site, r.event.label) for r in grid.readings if r.state == ABSENT_TABLE},
        key=lambda t: (t[0], t[1]),
    )
    warnings: list[str] = []
    if dupes:
        warnings.append(f"ERROR: {dupes} duplicate site/event/phase/parameter keys in the CSV")
    if len(grid.readings) != len(readings) + states[ABSENT_TABLE]:
        warnings.append("ERROR: grid has cells that are neither CSV rows nor absent-table fills")
    for r in readings:
        if r.state == NUMERIC and r.parameter == "pH" and not 0 <= r.value <= 14:
            warnings.append(f"ERROR: impossible pH {r.value} at {r.site} {r.event.label} {r.phase}")
        if r.state == NUMERIC and r.value is not None and r.value < 0:
            warnings.append(f"ERROR: negative value {r.value} for {r.parameter} at {r.site}")
    for site, info in grid.site_info.items():
        if info["confidence"] != "high":
            warnings.append(f"WARNING: site match confidence '{info['confidence']}' for {site}")
    for site, label in absent:
        warnings.append(f"WARNING: no table for {site} in {label}")
    by_site_event: dict[tuple[str, Event], Counter] = defaultdict(Counter)
    for r in grid.readings:
        by_site_event[(r.site, r.event)][r.state] += 1
    for (site, e), c in by_site_event.items():
        if c[ABSENT_TABLE] == 0 and c[NOT_SAMPLED] >= 12:
            warnings.append(f"WARNING: {site} {e.label}: {c[NOT_SAMPLED]} cells not sampled")
    return ValidationReport(len(readings), len(grid.readings), dict(states), dupes, absent, warnings)
