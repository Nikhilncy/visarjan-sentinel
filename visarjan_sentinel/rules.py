"""CPCB water-quality limits and the status of each reading against them.

Limits are read from the supplied cpcb_water_quality_criteria.csv, never typed
in by hand. Only Class B (outdoor bathing) is used for scoring. Parameters the
reports measured but CPCB sets no Class B limit for (COD, solids, turbidity,
conductivity, the four metals) get status NO_LIMIT and are shown, not scored.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .loader import ABSENT_TABLE, BDL, NOT_SAMPLED, NUMERIC, Reading

EXCEEDS = "exceeds"
WITHIN = "within"
STATUS_BDL = "bdl"
MISSING = "missing"
NO_LIMIT = "no_limit"

SCORING_CLASS = "B"

# CPCB parameter name -> parameter name in the readings CSV.
# None means the reports never measured it.
CPCB_TO_CSV = {
    "pH": "pH",
    "Dissolved oxygen": "Dissolved oxygen",
    "BOD (5 days 20C)": "BOD",
    "Total coliform": None,
}


@dataclass(frozen=True)
class Limit:
    parameter: str  # CSV name
    cpcb_parameter: str
    limit_type: str  # min | max | range
    low: float | None
    high: float | None
    unit: str

    def describe(self) -> str:
        if self.limit_type == "min":
            return f"at least {self.low:g} {self.unit}".strip()
        if self.limit_type == "max":
            return f"at most {self.high:g} {self.unit}".strip()
        return f"between {self.low:g} and {self.high:g}"

    def is_within(self, value: float) -> bool:
        if self.limit_type == "min":
            return value >= self.low
        if self.limit_type == "max":
            return value <= self.high
        return self.low <= value <= self.high


@dataclass(frozen=True)
class LimitSet:
    water_class: str
    designated_use: str
    limits: dict[str, Limit]  # keyed by CSV parameter name
    untested: list[str]  # CPCB parameters with a limit that the reports never measured

    @property
    def scored_parameters(self) -> list[str]:
        return list(self.limits)


def _parse_limit(parameter: str, row: dict[str, str]) -> Limit:
    kind = row["limit_type"].strip()
    raw = row["limit"].strip()
    if kind == "range":
        lo, hi = (float(x) for x in raw.split("-"))
        return Limit(parameter, row["parameter"], kind, lo, hi, row["unit"].strip())
    if kind == "min":
        return Limit(parameter, row["parameter"], kind, float(raw), None, row["unit"].strip())
    if kind == "max":
        return Limit(parameter, row["parameter"], kind, None, float(raw), row["unit"].strip())
    raise ValueError(f"Unknown limit_type {kind!r} for {parameter}")


def load_limits(path: Path, water_class: str = SCORING_CLASS) -> LimitSet:
    limits: dict[str, Limit] = {}
    untested: list[str] = []
    use = ""
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["class"].strip() != water_class:
                continue
            use = row["designated_best_use"].strip()
            cpcb_name = row["parameter"].strip()
            if cpcb_name not in CPCB_TO_CSV:
                raise ValueError(f"CPCB parameter {cpcb_name!r} has no mapping in rules.CPCB_TO_CSV")
            csv_name = CPCB_TO_CSV[cpcb_name]
            if csv_name is None:
                untested.append(cpcb_name)
                continue
            limits[csv_name] = _parse_limit(csv_name, row)
    if not limits:
        raise ValueError(f"No class {water_class} limits found in {path}")
    return LimitSet(water_class, use, limits, untested)


def status_of(reading: Reading, limits: LimitSet) -> str:
    """Status of one reading. Missing never counts as within, BDL never counts as a number."""
    if reading.state in (NOT_SAMPLED, ABSENT_TABLE):
        return MISSING
    limit = limits.limits.get(reading.parameter)
    if limit is None:
        return NO_LIMIT
    if reading.state == BDL:
        return STATUS_BDL
    assert reading.state == NUMERIC and reading.value is not None
    return WITHIN if limit.is_within(reading.value) else EXCEEDS
