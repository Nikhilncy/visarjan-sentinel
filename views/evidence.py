"""Page 4: verify conclusions against the source material."""

import pandas as pd
import streamlit as st

from visarjan_sentinel.ranking import TIER1_DO_THRESHOLD
from visarjan_sentinel.sources import COLIFORM_NOTE, GLOSSARY, REPORTS, SITE_MATCH_WARNING, UNITS_NOTE
from visarjan_sentinel.ui import charts, data, state
from visarjan_sentinel.ui import theme as T
from visarjan_sentinel.ui.data import DO, SCORED, STATE_LABEL

m = data.get_model()
site = state.selected_site(m)
ev = m.evidence

T.page_header("Evidence & Data Gaps", "Every reading with the report and PDF page it came from, and where evidence is missing.")

for key, val in (("ev_years", list(m.years)), ("ev_fests", ["Ganesh", "Durga"]), ("ev_phases", ["pre", "during", "after"]),
                 ("ev_types", list(STATE_LABEL.values()))):
    if key not in st.session_state:
        st.session_state[key] = val
f1, f2, f3 = st.columns([4, 5, 3], vertical_alignment="bottom")
with f1:
    ghats = st.multiselect("Ghat", options=m.sites, default=[site], format_func=lambda s: f"{m.rank_of[s]} · {s}")
with f2:
    params = st.multiselect("Test", options=list(dict.fromkeys(ev["parameter"])), default=SCORED)
with f3:
    query = st.text_input("Search", placeholder="site, test, report, page…", key="evidence_search")
f4, f5, f6 = st.columns([5, 4, 3], vertical_alignment="bottom")
with f4:
    years = st.pills("Year", options=m.years, selection_mode="multi", key="ev_years") or m.years
with f5:
    phases = st.pills("Phase", options=["pre", "during", "after"], selection_mode="multi", key="ev_phases",
                      format_func=lambda p: {"pre": "before", "during": "during", "after": "after"}[p]) or ["pre", "during", "after"]
with f6:
    fests = st.pills("Festival", options=["Ganesh", "Durga"], selection_mode="multi", key="ev_fests") or ["Ganesh", "Durga"]
types = st.pills("Record type", options=list(STATE_LABEL.values()), selection_mode="multi", key="ev_types",
                 format_func=lambda v: v.replace(" (below detection limit)", "")) or list(STATE_LABEL.values())

d = ev[ev["site"].isin(ghats) & ev["parameter"].isin(params) & ev["year"].isin(years)
       & ev["festival"].isin(fests) & ev["phase"].isin(phases) & ev["Record type"].isin(types)].copy()
if query:
    q = query.strip().lower()
    hay = (d["site"] + " " + d["site_as_printed"] + " " + d["parameter"] + " " + d["parameter_as_printed"] + " "
           + d["report_file"] + " " + d["source_page"] + " " + d["Reading"] + " " + d["Event"]).str.lower()
    d = d[hay.str.contains(q, regex=False)]


def _status(r) -> str:
    if r["status"] == "missing":
        return "missing"
    if r["status"] == "exceeds":
        return "critical (DO below 2 mg/l)" if r["parameter"] == DO and r["value_num"] < TIER1_DO_THRESHOLD else "outside limit"
    if r["status"] == "within":
        return "within limit"
    if r["status"] == "bdl":
        return "BDL"
    return "no Class B limit"


d["Status"] = d.apply(_status, axis=1)
d["Caveat"] = ["Medium-confidence site match; may be two places" if c != "high" else "" for c in d["site_match_confidence"]]
d["Page"] = d["source_page"].replace("", "no table")
d["Applicable limit"] = d["class_b_limit"].replace("", "none set")
d["Unit"] = d["unit_assumed"].replace("", "pH units")
counts = d["Record type"].value_counts()
st.markdown(
    f'<div class="vs-lead">{len(d)} records: ' + ", ".join(f"{v} {k.lower()}" for k, v in counts.items())
    + ". Red = critical, amber = outside the limit, grey italic = missing evidence.</div>", unsafe_allow_html=True)

show = d[["site", "site_as_printed", "year", "festival", "Phase", "parameter", "parameter_as_printed", "Reading", "Unit",
          "Applicable limit", "Status", "Record type", "report_file", "Page", "Caveat"]].rename(columns={
    "site": "Ghat", "site_as_printed": "Site as printed", "year": "Year", "festival": "Festival", "parameter": "Test",
    "parameter_as_printed": "Test as printed", "report_file": "Report"})
show["Site as printed"] = show["Site as printed"].replace("", "(no table)")
show["Test as printed"] = show["Test as printed"].replace("", "(no table)")


def _css(v: str) -> str:
    if v.startswith("critical"):
        return f"background-color:{T.RED_BG}; color:{T.RED}; font-weight:600"
    if v == "outside limit":
        return f"background-color:{T.AMBER_BG}; color:{T.AMBER_TX}; font-weight:600"
    if v == "missing":
        return f"background-color:{T.GREY_BG}; color:{T.MUTED}; font-style:italic"
    if v == "BDL":
        return f"color:{T.MUTED}"
    return ""


st.dataframe(show.style.map(_css, subset=["Status"]), hide_index=True, width="stretch",
             height=min(36 * (len(show) + 1) - 4, 560), row_height=36,
             column_config={"Year": st.column_config.NumberColumn(format="%d", width=70),
                            "Ghat": st.column_config.TextColumn(width=200), "Site as printed": st.column_config.TextColumn(width=240),
                            "Report": st.column_config.TextColumn(width=260), "Caveat": st.column_config.TextColumn(width=240)})
st.markdown(f'<div class="vs-lead">{UNITS_NOTE} {COLIFORM_NOTE}</div>', unsafe_allow_html=True)

T.section("Where evidence is missing", "Festival events and phases with no sample or no table, for the first ghat in the filter. "
          "A gap is unknown water, not clean water.")
first = ghats[0] if ghats else site
g = m.by_site[first]
T.legend(list(charts.GRID_COLORS.items()))
gc1, gc2 = st.columns([3, 2])
with gc1:
    st.altair_chart(charts.coverage_grid(m, first), width="stretch")
with gc2:
    st.markdown(f'<div class="vs-label">{first}</div><div class="vs-body">{data.coverage_sentence(m, g)}'
                + ("<ul>" + "".join(f"<li>{x}</li>" for x in data.gap_lines(g)) + "</ul>" if data.gap_lines(g) else " No gaps.")
                + "</div>", unsafe_allow_html=True)
    if g["site_match_confidence"] != "high":
        st.warning(SITE_MATCH_WARNING)

T.section("What the record types mean")
for k in ("Numeric zero", "BDL", "Not sampled", "Absent table", "Historical reading"):
    st.markdown(f"**{k}.** {GLOSSARY[k]}")

T.section("Source reports", "Page numbers above are PDF page numbers in these files.")
st.dataframe(pd.DataFrame([{"Report": r.title, "File": r.file_name, "PDF pages": r.pages, "Link": r.url}
                           for _, r in sorted(REPORTS.items())]),
             hide_index=True, width="stretch",
             column_config={"Link": st.column_config.LinkColumn(display_text="MPPCB download"),
                            "Report": st.column_config.TextColumn(width=330)})
