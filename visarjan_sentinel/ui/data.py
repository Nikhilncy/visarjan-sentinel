"""Load the validated pipeline output once and expose it as a small read-only model.

Everything numeric comes from visarjan_sentinel.build.run (loader, rules, ranking).
This module only reshapes it for display and writes plain-language sentences
from the numbers it is given. It never computes a score.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import pandas as pd
import streamlit as st

from visarjan_sentinel import build
from visarjan_sentinel.brief import _zero_do_citations
from visarjan_sentinel.config import CONTEXT
from visarjan_sentinel.ranking import TIER1_DO_THRESHOLD
from visarjan_sentinel.sources import GHAT_SHORT_NAMES, OUTPUT_DIR, PHASE_LABELS, PHASES

from . import theme as T

DO, BOD, PH = "Dissolved oxygen", "BOD", "pH"
SCORED = [DO, BOD, PH]
STATE_LABEL = {"numeric": "Numeric reading", "bdl": "BDL (below detection limit)",
               "not_sampled": "Not sampled", "absent_table": "Absent table"}


@st.cache_data(show_spinner="Reading the MPPCB data and computing the ranking…")
def load_everything() -> tuple[dict, dict, pd.DataFrame]:
    result = build.run(readings_csv=CONTEXT.readings_csv, cpcb_csv=CONTEXT.cpcb_csv)
    ev = pd.read_csv(OUTPUT_DIR / "evidence.csv", keep_default_na=False, dtype=str)
    ev["value_num"] = pd.to_numeric(ev["value"], errors="coerce")
    ev["year"] = ev["year"].astype(int)
    ev["Event"] = ev["festival"] + " " + ev["year"].astype(str)
    ev["Phase"] = ev["phase"].map(PHASE_LABELS)
    ev["Record type"] = ev["state"].map(STATE_LABEL)
    ev["Reading"] = [cell_text(s, v, p) for s, v, p in zip(ev["state"], ev["value_num"], ev["value_as_printed"])]
    return result["ranking"], result["validation"], ev


def cell_text(state: str, value_num: float, value_as_printed: str) -> str:
    if state == "numeric":
        return f"{value_num:g}"
    if state == "bdl":
        return value_as_printed or "BDL"
    if state == "not_sampled":
        return "not sampled"
    return "no table"


def short(site: str) -> str:
    return GHAT_SHORT_NAMES.get(site, site)


def _category(row) -> str:
    if row["status"] == "missing":
        return T.CAT_MISS
    if row["status"] == "exceeds":
        if row["parameter"] == DO and row["value_num"] < TIER1_DO_THRESHOLD:
            return T.CAT_CRIT
        return T.CAT_OUT
    return T.CAT_IN


@dataclass
class Model:
    ranking: dict
    validation: dict
    evidence: pd.DataFrame
    scored: pd.DataFrame  # DO, BOD, pH cells with a display Category

    @property
    def ghats(self) -> list[dict]:
        return self.ranking["ghats"]

    @property
    def sites(self) -> list[str]:
        return [g["site"] for g in self.ghats]

    @property
    def by_site(self) -> dict[str, dict]:
        return {g["site"]: g for g in self.ghats}

    @property
    def rank_of(self) -> dict[str, int]:
        return {g["site"]: g["rank"] for g in self.ghats}

    @property
    def limits(self) -> dict:
        return self.ranking["limits"]

    @property
    def do_lim(self) -> float:
        return self.limits[DO]["low"]

    @property
    def bod_lim(self) -> float:
        return self.limits[BOD]["high"]

    @property
    def events(self) -> list[str]:
        return self.ranking["events"]

    @property
    def years(self) -> list[int]:
        return sorted({int(e.split()[-1]) for e in self.events})

    @property
    def period(self) -> str:
        y = self.years
        return f"{y[0]} to {y[-1]}" if len(y) > 1 else str(y[0])

    @property
    def last_year(self) -> int:
        return self.years[-1]

    @property
    def tier1(self) -> list[dict]:
        return [g for g in self.ghats if g["tier"] == 1]

    @property
    def n_incomplete(self) -> int:
        return sum(1 for g in self.ghats if g["coverage"]["sampled"] < g["coverage"]["expected"])

    @property
    def totals(self) -> tuple[int, int]:
        return sum(g["exceedances"] for g in self.ghats), sum(g["numeric_scored"] for g in self.ghats)

    def label(self, site: str) -> str:
        return f"{self.rank_of[site]}  {short(site)}"

    @property
    def label_order(self) -> list[str]:
        return [self.label(s) for s in self.sites]

    def limit_text(self, param: str) -> str:
        return self.limits[param]["rule"]


def get_model() -> Model:
    ranking, validation, ev = load_everything()
    rank_of = {g["site"]: g["rank"] for g in ranking["ghats"]}
    scored = ev[ev["parameter"].isin(SCORED)].copy()
    scored["Category"] = scored.apply(_category, axis=1)
    scored["Ghat"] = scored["site"].map(short)
    scored["Rank"] = scored["site"].map(rank_of)
    scored["Ghat label"] = scored["Rank"].astype(str) + "  " + scored["Ghat"]
    return Model(ranking, validation, ev, scored)


# ----------------------------------------------------------------------------- plain language
def why_lines(m: Model, g: dict) -> list[str]:
    """Reasons as sentences. Every number is copied from the ranking output."""
    pp = g["per_parameter"]
    out: list[str] = []
    do = pp[DO]
    if do["numeric"]:
        out.append(f"<strong>{do['exceedances']} of {do['numeric']}</strong> dissolved-oxygen readings were below "
                   f"{m.do_lim:g} mg/l, the Class B minimum for bathing water. Fish and other aquatic life need oxygen.")
        if g["zero_do_count"]:
            out.append(f"<strong>{g['zero_do_count']}</strong> of them read <strong>0 mg/l</strong>, no oxygen at all "
                       f"({_zero_do_citations(g, 'en')}).")
        elif g["min_do"] is not None and g["min_do"] < m.do_lim:
            out.append(f"The lowest was <strong>{g['min_do']:g} mg/l</strong> ({g['min_do_citation']}).")
    else:
        out.append("No numeric dissolved-oxygen reading exists for this ghat.")
    bod = pp[BOD]
    if bod["numeric"]:
        s = (f"<strong>{bod['exceedances']} of {bod['numeric']}</strong> BOD readings were above {m.bod_lim:g} mg/l. "
             "Higher BOD means organic matter is using up more of the oxygen.")
        if bod["worst_value"] is not None:
            s += f" Highest <strong>{bod['worst_value']:g} mg/l</strong> ({bod['worst_citation']})."
        out.append(s)
    ph = pp[PH]
    if ph["numeric"]:
        lo, hi = m.limits[PH]["low"], m.limits[PH]["high"]
        if ph["exceedances"]:
            out.append(f"<strong>{ph['exceedances']} of {ph['numeric']}</strong> pH readings fell outside {lo:g} to {hi:g} "
                       f"(furthest {ph['worst_value']:g}, {ph['worst_citation']}).")
        else:
            out.append(f"All {ph['numeric']} pH readings were within {lo:g} to {hi:g}. One parameter only, not a safety rating.")
    return out


def concise_reason(m: Model, g: dict) -> str:
    do, bod = g["per_parameter"][DO], g["per_parameter"][BOD]
    s = f"DO below {m.do_lim:g} mg/l in {do['exceedances']} of {do['numeric']} readings"
    if g["zero_do_count"]:
        s += f", including 0 mg/l {g['zero_do_count']} time{'s' if g['zero_do_count'] != 1 else ''}"
    elif g["min_do"] is not None:
        s += f", lowest {g['min_do']:g}"
    s += f". BOD above {m.bod_lim:g} mg/l in {bod['exceedances']} of {bod['numeric']}."
    return s


def outside_sentence(g: dict) -> str:
    return f"{g['exceedances']} of {g['numeric_scored']} scored readings were outside the applicable limits"


def coverage_sentence(m: Model, g: dict) -> str:
    c = g["coverage"]
    return (f"{c['sampled']} of {c['expected']} expected readings exist ({c['sampled_share']:.0%}). Expected = "
            f"{len(m.events)} festival events × 3 phases × the tests printed for each event. "
            f"{c['not_sampled']} not sampled, {c['absent_table']} in absent tables, {c['bdl']} metals reported BDL.")


def gap_lines(g: dict) -> list[str]:
    gaps = [f"{e['festival']} {e['year']}: no table in the report" for e in g["events"] if not e["table_present"]]
    gaps += [f"{e['festival']} {e['year']}: {e['not_sampled']} reading{'s' if e['not_sampled'] != 1 else ''} not sampled"
             for e in g["events"] if e["table_present"] and e["not_sampled"]]
    return gaps


def recommendation(m: Model, g: dict) -> str:
    """Deterministic decision-support text from the tier and the latest readings. Not an order."""
    when = f"before {CONTEXT.event_date_en}" if CONTEXT.event_date else "before the next immersion"
    if g["tier"] == 1:
        n = g["do_below_tier1_count"]
        return (f"Sample DO, BOD and pH at this ghat {when} and give it priority for cleaning and aeration "
                f"resources. Basis: dissolved oxygen was recorded below {TIER1_DO_THRESHOLD:g} mg/l "
                f"{n} time{'s' if n != 1 else ''} in {m.period}.")
    r = g["recent"]
    if r["min_do"] is not None and r["min_do"] < m.do_lim:
        return (f"Monitor dissolved oxygen during immersion and sample all three phases. Basis: DO fell to "
                f"{r['min_do']:g} mg/l in {g['recent_year']}, below the {m.do_lim:g} mg/l minimum.")
    bod = g["per_parameter"][BOD]
    return (f"Continue three-phase sampling (before, during, one week after) and add total coliform. Basis: no DO "
            f"reading below {m.do_lim:g} mg/l in {g['recent_year']}, but BOD was above the limit in "
            f"{bod['exceedances']} of {bod['numeric']} readings overall.")


def badges_for(m: Model, g: dict, include_green: bool = True) -> str:
    b = T.badge("Priority tier 1", "red") if g["tier"] == 1 else T.badge("Tier 2")
    b += T.badge(f"Rank {g['rank']} of {len(m.sites)}")
    if g["site_match_confidence"] != "high":
        b += T.badge("site match: medium confidence", "amber")
    ph = g["per_parameter"][PH]
    if include_green and ph["numeric"] and ph["exceedances"] == 0:
        b += T.badge("pH within range on every reading (this parameter only)", "green")
    return b


def today() -> dt.date:
    return dt.date.today()
