"""Rank the seven ghats for follow-up priority.

Scoring rule (approved design, kept deliberately simple and visible):

  1. Scored parameters: the Class B parameters that were actually measured,
     dissolved oxygen (DO), BOD and pH.
  2. For each ghat, exceedance share =
         numeric readings outside the Class B limit
       / numeric readings of the scored parameters
     over every year, festival and phase in the data. Missing and BDL readings
     are in neither the numerator nor the denominator.
  3. Severity tier: any numeric DO reading below 2 mg/l (this includes 0)
     puts the ghat in Tier 1, the highest follow-up priority. Everything else
     is Tier 2.
  4. Order: tier, then exceedance share (high first), then lowest recorded DO
     (low first), then name for a stable result.

Coverage (how much of the expected grid was actually sampled) is reported next
to the score and never folded into it.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field

from .loader import ABSENT_TABLE, BDL, NOT_SAMPLED, NUMERIC, Event, Grid, Reading
from .rules import EXCEEDS, LimitSet, status_of
from .sources import PHASE_LABELS, PHASES, SITE_MATCH_WARNING

DO = "Dissolved oxygen"
TIER1_DO_THRESHOLD = 2.0  # mg/l, strictly below

FORMULA_TEXT = (
    "Exceedance share = readings outside CPCB Class B limits / numeric readings of "
    "DO, BOD and pH, over 2023 to 2025, Ganesh and Durga, all three phases. "
    f"Tier 1 = any DO reading below {TIER1_DO_THRESHOLD:g} mg/l (including 0). "
    "Order = tier, then exceedance share, then lowest recorded DO. "
    "Missing and BDL readings are left out of both numerator and denominator. "
    "Coverage is shown separately and does not change the score."
)

LIMITATIONS = [
    "Historical readings from 2023 to 2025 only. They do not describe water quality today.",
    "One sample per phase per event. No replicates, no sampling dates in the data.",
    "Only DO, BOD and pH have a CPCB Class B limit and were measured. Total coliform, "
    "also a Class B requirement, was never tested, so full Class B compliance is unknown.",
    "COD, solids, turbidity, conductivity and metals are shown but not scored: CPCB "
    "sets no Class B limit for them.",
    "Metal detection limits and methods appear to differ between years. Metal values are "
    "not comparable across years and are reported only as printed.",
    "Units are not printed in the reports. Standard units are assumed.",
    "The ranking says where to send follow-up testing and cleaning first. It is not a "
    "statement about health effects or about whether any ghat is safe.",
]


@dataclass
class Coverage:
    expected: int = 0
    numeric: int = 0
    bdl: int = 0
    not_sampled: int = 0
    absent_table: int = 0

    @property
    def sampled(self) -> int:
        return self.numeric + self.bdl

    @property
    def sampled_share(self) -> float:
        return self.sampled / self.expected if self.expected else 0.0

    def add(self, r: Reading) -> None:
        self.expected += 1
        if r.state == NUMERIC:
            self.numeric += 1
        elif r.state == BDL:
            self.bdl += 1
        elif r.state == NOT_SAMPLED:
            self.not_sampled += 1
        elif r.state == ABSENT_TABLE:
            self.absent_table += 1

    def to_dict(self) -> dict:
        d = asdict(self)
        d["sampled"] = self.sampled
        d["sampled_share"] = round(self.sampled_share, 4)
        return d


@dataclass
class ParameterTally:
    parameter: str
    exceedances: int = 0
    numeric: int = 0
    worst_value: float | None = None
    worst_citation: str = ""

    @property
    def share(self) -> float:
        return self.exceedances / self.numeric if self.numeric else 0.0


@dataclass
class EventSummary:
    """What one report says about one ghat in one festival."""

    year: int
    festival: str
    table_present: bool
    pages: list[int]
    report_file: str
    exceedances: int
    numeric_scored: int
    not_sampled: int
    do_by_phase: dict[str, str]  # phase -> value as text or state
    bod_by_phase: dict[str, str]
    ph_by_phase: dict[str, str]


@dataclass
class GhatScore:
    site: str
    water_body: str
    site_match_confidence: str
    tier: int
    rank: int
    exceedance_share: float
    exceedances: int
    numeric_scored: int
    min_do: float | None
    min_do_citation: str
    zero_do_count: int
    do_below_tier1_count: int
    per_parameter: dict[str, ParameterTally]
    coverage: Coverage
    scored_coverage: Coverage
    recent_year: int
    recent: "GhatWindow"
    events: list[EventSummary]
    warnings: list[str]
    reason: str
    tier_reason: str

    def to_dict(self) -> dict:
        return {
            "site": self.site,
            "water_body": self.water_body,
            "site_match_confidence": self.site_match_confidence,
            "tier": self.tier,
            "rank": self.rank,
            "exceedance_share": round(self.exceedance_share, 4),
            "exceedances": self.exceedances,
            "numeric_scored": self.numeric_scored,
            "min_do": self.min_do,
            "min_do_citation": self.min_do_citation,
            "zero_do_count": self.zero_do_count,
            "do_below_tier1_count": self.do_below_tier1_count,
            "per_parameter": {
                k: {**asdict(v), "share": round(v.share, 4)} for k, v in self.per_parameter.items()
            },
            "coverage": self.coverage.to_dict(),
            "scored_coverage": self.scored_coverage.to_dict(),
            "recent_year": self.recent_year,
            "recent": self.recent.to_dict(),
            "events": [asdict(e) for e in self.events],
            "warnings": self.warnings,
            "reason": self.reason,
            "tier_reason": self.tier_reason,
        }


@dataclass
class GhatWindow:
    """Exceedance and coverage figures for a subset of events (used for 'recent')."""

    label: str
    exceedances: int = 0
    numeric_scored: int = 0
    min_do: float | None = None
    coverage: Coverage = field(default_factory=Coverage)

    @property
    def share(self) -> float:
        return self.exceedances / self.numeric_scored if self.numeric_scored else 0.0

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "exceedances": self.exceedances,
            "numeric_scored": self.numeric_scored,
            "exceedance_share": round(self.share, 4),
            "min_do": self.min_do,
            "coverage": self.coverage.to_dict(),
        }


def _cell_text(r: Reading | None) -> str:
    if r is None:
        return "absent"
    if r.state == NUMERIC:
        return f"{r.value:g}"
    if r.state == BDL:
        return "BDL"
    if r.state == NOT_SAMPLED:
        return "not sampled"
    return "no table"


def _fmt_pages(pages: list[int]) -> str:
    return ", ".join(f"p.{p}" for p in sorted(set(pages)))


def _build_reason(tally: dict[str, ParameterTally], limits: LimitSet, zero_do: list[Reading],
                  below: list[Reading], absent: list[Event], not_sampled_events: dict[Event, int]) -> str:
    parts: list[str] = []
    order = [DO, "BOD", "pH"]
    for p in order:
        if p not in tally:
            continue
        t = tally[p]
        lim = limits.limits[p]
        name = {DO: "dissolved-oxygen", "BOD": "BOD", "pH": "pH"}[p]
        if t.numeric == 0:
            parts.append(f"No numeric {name} readings.")
            continue
        verb = {"min": "below", "max": "above", "range": "outside"}[lim.limit_type]
        sentence = f"{t.exceedances} of {t.numeric} {name} readings {verb} the Class B limit ({lim.describe()})"
        if p == DO and zero_do:
            cites = defaultdict(list)
            for r in zero_do:
                cites[r.event.year].append(r.source_page)
            cite_txt = "; ".join(f"{y} report {_fmt_pages(pg)}" for y, pg in sorted(cites.items()))
            sentence += f", including 0 mg/l {len(zero_do)} time{'s' if len(zero_do) != 1 else ''} ({cite_txt})"
        elif p == DO and below:
            worst = min(below, key=lambda r: r.value)
            sentence += f", lowest {worst.value:g} mg/l ({worst.event.label}, {worst.phase}, {worst.event.year} report p.{worst.source_page})"
        parts.append(sentence + ".")
    gaps = []
    for e in absent:
        gaps.append(f"no {e.label} table in the report")
    for e, n in sorted(not_sampled_events.items(), key=lambda kv: kv[0].sort_key):
        gaps.append(f"{n} reading{'s' if n != 1 else ''} not sampled in {e.label}")
    if gaps:
        parts.append("Data gaps: " + "; ".join(gaps) + ".")
    return " ".join(parts)


def score_ghat(site: str, grid: Grid, limits: LimitSet, recent_year: int) -> GhatScore:
    readings = grid.for_site(site)
    info = grid.site_info[site]
    tally: dict[str, ParameterTally] = {p: ParameterTally(p) for p in limits.scored_parameters}
    coverage, scored_cov = Coverage(), Coverage()
    recent = GhatWindow(label=f"{recent_year} only")
    zero_do: list[Reading] = []
    below_tier1: list[Reading] = []
    min_do: Reading | None = None
    not_sampled_by_event: dict[Event, int] = defaultdict(int)

    for r in readings:
        coverage.add(r)
        is_recent = r.event.year == recent_year
        if is_recent:
            recent.coverage.add(r)
        if r.state == NOT_SAMPLED:
            not_sampled_by_event[r.event] += 1
        if r.parameter not in tally:
            continue
        scored_cov.add(r)
        st = status_of(r, limits)
        t = tally[r.parameter]
        if r.state == NUMERIC:
            t.numeric += 1
            if is_recent:
                recent.numeric_scored += 1
            if st == EXCEEDS:
                t.exceedances += 1
                if is_recent:
                    recent.exceedances += 1
                lim = limits.limits[r.parameter]
                # "worst" = furthest outside the limit
                dist = (lim.low - r.value) if lim.limit_type == "min" else (
                    r.value - lim.high if lim.limit_type == "max" else max(lim.low - r.value, r.value - lim.high))
                prev = t.worst_value
                if prev is None or dist > (
                    (lim.low - prev) if lim.limit_type == "min" else (
                        prev - lim.high if lim.limit_type == "max" else max(lim.low - prev, prev - lim.high))):
                    t.worst_value, t.worst_citation = r.value, r.citation
            if r.parameter == DO:
                if min_do is None or r.value < min_do.value:
                    min_do = r
                if is_recent and (recent.min_do is None or r.value < recent.min_do):
                    recent.min_do = r.value
                if r.value == 0:
                    zero_do.append(r)
                if r.value < TIER1_DO_THRESHOLD:
                    below_tier1.append(r)

    exceedances = sum(t.exceedances for t in tally.values())
    numeric = sum(t.numeric for t in tally.values())
    share = exceedances / numeric if numeric else 0.0

    absent_events = sorted({r.event for r in readings if r.state == ABSENT_TABLE}, key=lambda e: e.sort_key)
    tier = 1 if below_tier1 else 2
    if tier == 1:
        tier_reason = (
            f"Tier 1: {len(below_tier1)} dissolved-oxygen reading{'s' if len(below_tier1) != 1 else ''} "
            f"below {TIER1_DO_THRESHOLD:g} mg/l, lowest {min_do.value:g} mg/l ({min_do.citation})."
        )
    else:
        tier_reason = f"Tier 2: no dissolved-oxygen reading below {TIER1_DO_THRESHOLD:g} mg/l."

    events: list[EventSummary] = []
    for e in grid.events:
        rows = [r for r in readings if r.event == e]
        present = any(r.state != ABSENT_TABLE for r in rows)
        pages = sorted({r.source_page for r in rows if r.source_page is not None})
        ev_exc = sum(1 for r in rows if r.parameter in tally and status_of(r, limits) == EXCEEDS)
        ev_num = sum(1 for r in rows if r.parameter in tally and r.state == NUMERIC)
        ev_ns = sum(1 for r in rows if r.state == NOT_SAMPLED)

        def by_phase(param: str) -> dict[str, str]:
            return {ph: _cell_text(grid.lookup(site, e, ph, param)) for ph in PHASES}

        events.append(EventSummary(e.year, e.festival, present, pages, grid_report_file(e), ev_exc, ev_num, ev_ns,
                                   by_phase(DO), by_phase("BOD"), by_phase("pH")))

    warnings: list[str] = []
    if info["confidence"] != "high":
        warnings.append(SITE_MATCH_WARNING)
    for e in absent_events:
        warnings.append(f"No {e.label} table in the {e.year} report. This event is unsampled, not clean.")
    for e, n in sorted(not_sampled_by_event.items(), key=lambda kv: kv[0].sort_key):
        phases_missing = sorted({r.phase for r in readings if r.event == e and r.state == NOT_SAMPLED},
                                key=PHASES.index)
        warnings.append(
            f"{e.label}: {n} reading{'s' if n != 1 else ''} not sampled "
            f"({', '.join(PHASE_LABELS[p] for p in phases_missing)}). Missing, not clean."
        )

    reason = _build_reason(tally, limits, zero_do, below_tier1, absent_events, dict(not_sampled_by_event))

    return GhatScore(
        site=site,
        water_body=info["water_body"],
        site_match_confidence=info["confidence"],
        tier=tier,
        rank=0,
        exceedance_share=share,
        exceedances=exceedances,
        numeric_scored=numeric,
        min_do=min_do.value if min_do else None,
        min_do_citation=min_do.citation if min_do else "",
        zero_do_count=len(zero_do),
        do_below_tier1_count=len(below_tier1),
        per_parameter=tally,
        coverage=coverage,
        scored_coverage=scored_cov,
        recent_year=recent_year,
        recent=recent,
        events=events,
        warnings=warnings,
        reason=reason,
        tier_reason=tier_reason,
    )


def grid_report_file(e: Event) -> str:
    from .sources import REPORTS

    return REPORTS[e.year].file_name


def rank_ghats(grid: Grid, limits: LimitSet, recent_year: int | None = None) -> list[GhatScore]:
    if recent_year is None:
        recent_year = max(e.year for e in grid.events)
    scores = [score_ghat(s, grid, limits, recent_year) for s in grid.sites]
    scores.sort(
        key=lambda g: (
            g.tier,
            -g.exceedance_share,
            g.min_do if g.min_do is not None else float("inf"),
            g.site,
        )
    )
    for i, g in enumerate(scores, start=1):
        g.rank = i
    return scores
