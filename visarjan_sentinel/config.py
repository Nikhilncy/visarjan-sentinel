"""Reporting context: who the tool is for, which event it targets, which dataset it reads.

Loaded from settings.toml at the project root so the event, organisation and
source reports can change without touching the interface or the ranking code.
The years covered by the data are never configured; they are read from the data.
"""

from __future__ import annotations

import datetime as dt
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_FILE = PROJECT_ROOT / "settings.toml"

MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August",
             "September", "October", "November", "December"]
MONTHS_HI = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त",
             "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]


def date_en(d: dt.date) -> str:
    return f"{d.day} {MONTHS_EN[d.month - 1]} {d.year}"


def date_hi(d: dt.date) -> str:
    return f"{d.day} {MONTHS_HI[d.month - 1]} {d.year}"


@dataclass(frozen=True)
class Report:
    year: int
    file_name: str
    title: str
    pages: int
    url: str


@dataclass(frozen=True)
class Context:
    organisation: str
    organisation_short: str
    organisation_hi: str
    event_name: str
    event_name_hi: str
    event_date: dt.date
    readings_csv: Path
    cpcb_csv: Path
    source_label: str
    source_label_hi: str
    reports: dict[int, Report] = field(default_factory=dict)
    settings_path: Path | None = None

    @property
    def event_date_en(self) -> str:
        return date_en(self.event_date)

    @property
    def event_date_hi(self) -> str:
        return date_hi(self.event_date)

    @property
    def event_year(self) -> int:
        return self.event_date.year

    def days_until_event(self, today: dt.date | None = None) -> int:
        return (self.event_date - (today or dt.date.today())).days


def _as_date(v) -> dt.date:
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    return dt.date.fromisoformat(str(v))


def load_context(path: Path | None = None) -> Context:
    path = Path(path) if path else SETTINGS_FILE
    root = path.parent
    with open(path, "rb") as f:
        raw = tomllib.load(f)
    try:
        org, ev, ds = raw["organisation"], raw["target_event"], raw["dataset"]
        reports = {int(r["year"]): Report(int(r["year"]), r["file_name"], r["title"], int(r["pages"]), r["url"])
                   for r in raw.get("reports", [])}
        return Context(
            organisation=org["name"],
            organisation_short=org.get("short", org["name"]),
            organisation_hi=org.get("name_hi", org["name"]),
            event_name=ev["name"],
            event_name_hi=ev.get("name_hi", ev["name"]),
            event_date=_as_date(ev["date"]),
            readings_csv=(root / ds["readings_csv"]).resolve(),
            cpcb_csv=(root / ds["cpcb_csv"]).resolve(),
            source_label=ds["source_label"],
            source_label_hi=ds.get("source_label_hi", ds["source_label"]),
            reports=reports,
            settings_path=path,
        )
    except KeyError as exc:
        raise ValueError(f"settings.toml is missing a required key: {exc}") from exc


CONTEXT = load_context()
