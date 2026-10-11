"""Page 3: patterns and comparisons across historical measurements."""

import streamlit as st

from visarjan_sentinel.ranking import TIER1_DO_THRESHOLD
from visarjan_sentinel.sources import PARAMETER_MEANING, PHASE_LABELS, PHASES
from visarjan_sentinel.ui import charts, data, state
from visarjan_sentinel.ui import theme as T
from visarjan_sentinel.ui.data import BOD, DO, PH, SCORED

m = data.get_model()
site = state.selected_site(m)

T.page_header("Historical Analysis", f"How one ghat's readings compare with the Class B benchmark across {m.period}, "
              "by year and by sampling phase.")

if "ghat_select" not in st.session_state:
    st.session_state["ghat_select"] = site
if "years_select" not in st.session_state:
    st.session_state["years_select"] = list(m.years)
if "phases_select" not in st.session_state:
    st.session_state["phases_select"] = list(PHASES)
c1, c2 = st.columns([1, 1], vertical_alignment="bottom")
with c1:
    st.selectbox("Ghat", options=m.sites, key="ghat_select", format_func=lambda s: f"{m.rank_of[s]} · {s}",
                 on_change=lambda: state.set_site(st.session_state["ghat_select"]))
with c2:
    param = st.segmented_control("Test", options=SCORED, default=DO, key="param_select",
                                 format_func=lambda p: {DO: "Dissolved oxygen", BOD: "BOD", PH: "pH"}[p]) or DO
c3, c4 = st.columns([1, 1], vertical_alignment="bottom")
with c3:
    years_sel = st.pills("Years", options=m.years, selection_mode="multi", key="years_select") or m.years
with c4:
    phases_sel = st.pills("Phases", options=list(PHASES), selection_mode="multi", key="phases_select",
                          format_func=lambda p: {"pre": "before immersion", "during": "during", "after": "one week after"}[p]) or list(PHASES)
years_sel = sorted(years_sel)
phases_sel = [p for p in PHASES if p in phases_sel]
site = state.selected_site(m)
g = m.by_site[site]

unit = "" if param == PH else " mg/l"
bench = {DO: f"at least {m.do_lim:g} mg/l", BOD: f"at most {m.bod_lim:g} mg/l",
         PH: f"{m.limits[PH]['low']:g} to {m.limits[PH]['high']:g}"}[param]
extra = (f" The dotted red line at {TIER1_DO_THRESHOLD:g} mg/l is the ranking's critical threshold, not a CPCB limit."
         if param == DO else "")
st.markdown(f'<div class="vs-lead">{PARAMETER_MEANING[param]} CPCB Class B benchmark: <strong>{bench}</strong> '
            f"(dotted navy line{' or shaded band' if param == PH else ''}).{extra} n/s = not sampled or no table in the report, "
            "never treated as clean.</div>", unsafe_allow_html=True)
if g["site_match_confidence"] != "high":
    st.warning(g["warnings"][0])

sc_all = m.scored[(m.scored["site"] == site) & (m.scored["parameter"] == param)]
sc = sc_all[sc_all["year"].isin(years_sel) & sc_all["phase"].isin(phases_sel)]
present = sc[sc["Category"] != T.CAT_MISS]
filtered = len(sc) < len(sc_all)
label = {DO: "Dissolved oxygen", BOD: "BOD", PH: "pH"}[param]


def _summary(d) -> str:
    p = d[d["Category"] != T.CAT_MISS]
    miss = d[d["Category"] == T.CAT_MISS]
    if p.empty:
        return f"No numeric reading. {len(miss)} missing."
    out = p[p["Category"] != T.CAT_IN]
    s = f"<strong>{len(out)} of {len(p)}</strong> readings outside the limit."
    if param == DO:
        lo = p.loc[p["value_num"].idxmin()]
        s += f" Lowest <strong>{lo['value_num']:g} mg/l</strong> ({lo['Event']}, {lo['Phase']}, p.{lo['source_page']})."
    elif param == BOD:
        hi = p.loc[p["value_num"].idxmax()]
        s += f" Highest <strong>{hi['value_num']:g} mg/l</strong> ({hi['Event']}, {hi['Phase']}, p.{hi['source_page']})."
    else:
        s += f" Range {p['value_num'].min():g} to {p['value_num'].max():g}."
    if len(miss):
        ev = ", ".join(sorted({f"{r.Event} ({r.Reading})" for r in miss.itertuples()}))
        s += f" <span style='color:{T.MUTED}'>{len(miss)} missing: {ev}.</span>"
    return s


T.section(f"{label} by year, {site}", f"How many numeric readings fell outside the benchmark in each year ({m.period}). "
          "Missing readings are not counted here; see the phase charts and the evidence page for them."
          + (" Filters applied: the charts show only the selected years and phases." if filtered else ""))
T.legend([(T.CAT_CRIT, T.RED), (T.CAT_OUT, T.AMBER), (T.CAT_IN, T.TEAL)])
st.altair_chart(charts.year_chart(m, site, param, years_sel, phases_sel), width="stretch")
by_year = []
for y in years_sel:
    d = sc[sc["year"] == y]
    p = d[d["Category"] != T.CAT_MISS]
    out = p[p["Category"] != T.CAT_IN]
    by_year.append(f"<strong>{y}</strong>: {len(out)} of {len(p)} outside" + (f", {len(d) - len(p)} missing" if len(d) > len(p) else ""))
T.interpretation("What this shows. " + "; ".join(by_year) + ". " + _summary(sc))

T.section(f"{label} by sampling phase", "Before immersion, during, and one week after, for each festival event. "
          f"Values are printed on the bars; n/s marks a missing reading. Units: {label}{unit or ' (pH units)'}.")
T.status_legend()
vals = present["value_num"]
ref = {DO: m.do_lim, BOD: m.bod_lim, PH: m.limits[PH]["high"]}[param]
y_max = float(max(ref * 1.35, (vals.max() if len(vals) else 0) * 1.2))
for ph in [p for p in PHASES if p in phases_sel]:
    st.altair_chart(charts.phase_chart(m, site, param, ph, y_max, years_sel), width="stretch")
    T.interpretation(f"<strong>{PHASE_LABELS[ph].capitalize()}.</strong> " + _summary(sc[sc["phase"] == ph]))

T.section(f"All ghats compared: {label}", f"Every {label.lower()} reading at all {len(m.sites)} ghats, {m.period}, "
          "as dots against the benchmark. Grey text counts the readings that do not exist. Click a dot to choose that ghat.")
T.legend([(T.CAT_CRIT, T.RED), (T.CAT_OUT, T.AMBER), (T.CAT_IN, T.TEAL)], "Dotted line = Class B benchmark")
st.altair_chart(charts.strip_chart(m, param), width="stretch", key="strip_sel",
                on_select=state.chart_select_callback(m, "strip_sel"), selection_mode=["ghat_sel"])
allp = m.scored[(m.scored["parameter"] == param)]
num = allp[allp["Category"] != T.CAT_MISS]
out = num[num["Category"] != T.CAT_IN]
T.interpretation(f"Across all ghats, <strong>{len(out)} of {len(num)}</strong> numeric {label.lower()} readings were outside "
                 f"the benchmark and {len(allp) - len(num)} expected readings are missing. Historical readings; "
                 "they do not describe the water today.")
