"""Page 2: decide where to focus first."""

import streamlit as st

from visarjan_sentinel.ui import data, state
from visarjan_sentinel.ui import theme as T

m = data.get_model()
site = state.selected_site(m)

T.page_header("Ghat Priorities", f"All {len(m.sites)} ghats in the order produced by the ranking engine. "
              f"Historical readings, {m.period}; not current conditions.")


def _on_pills() -> None:
    if st.session_state.get("ghat_pills"):
        state.set_site(st.session_state["ghat_pills"])
    else:
        st.session_state["ghat_pills"] = state.selected_site(m)


if "ghat_pills" not in st.session_state:
    st.session_state["ghat_pills"] = site
st.pills("Choose a ghat", options=m.sites, format_func=lambda s: f"{m.rank_of[s]} · {data.short(s)}", key="ghat_pills",
         on_change=_on_pills, selection_mode="single", label_visibility="collapsed")
site = state.selected_site(m)

rows = []
for g in m.ghats:
    cls = ' class="sel"' if g["site"] == site else ""
    b = T.badge("Tier 1", "red") if g["tier"] == 1 else T.badge("Tier 2")
    if g["site_match_confidence"] != "high":
        b += T.badge("site match: medium", "amber")
    if g["coverage"]["absent_table"]:
        b += T.badge("festival table missing", "grey")
    low = "n/a" if g["min_do"] is None else f"{g['min_do']:g}"
    low_cls = "bad" if g["min_do"] is not None and g["min_do"] < m.do_lim else ""
    rows.append(
        f'<tr{cls}><td class="rk">{g["rank"]}</td><td class="nm">{g["site"]}<br>{b}</td>'
        f'<td>{data.concise_reason(m, g)}</td>'
        f'<td class="num">{g["exceedances"]} of {g["numeric_scored"]}</td>'
        f'<td class="num {low_cls}">{low} mg/l</td>'
        f'<td class="cov num">{g["coverage"]["sampled_share"]:.0%} · {g["coverage"]["sampled"]} of {g["coverage"]["expected"]}</td></tr>'
    )
st.markdown(
    '<table class="vs-queue"><thead><tr><th></th><th>Ghat</th><th>Why</th><th class="num">Outside limits</th>'
    '<th class="num">Lowest DO</th><th class="num">Evidence coverage</th></tr></thead>' + "".join(rows) + "</table>",
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="vs-lead" style="margin-top:8px">Outside limits = numeric DO, BOD and pH readings outside the CPCB Class B '
    f"limits, of all numeric readings of those tests, {m.period}. Lowest DO = lowest dissolved oxygen ever recorded; the "
    f"Class B minimum is {m.do_lim:g} mg/l and below 2 mg/l is the ranking's critical threshold. Evidence coverage = readings "
    f"that exist, of all readings the reports should contain ({len(m.events)} events × 3 phases × tests printed). "
    "Coverage never changes the rank.</div>",
    unsafe_allow_html=True,
)

g = m.by_site[site]
T.section(f"{g['site']}")
st.markdown(data.badges_for(m, g) + f'<span style="font-size:0.82rem;color:{T.MUTED}">{g["water_body"]}</span>',
            unsafe_allow_html=True)
for w in g["warnings"]:
    st.warning(w)
c1, c2, c3 = st.columns([5, 4, 4])
with c1:
    st.markdown('<div class="vs-label">Main finding</div><div class="vs-body"><ul>'
                + "".join(f"<li>{x}</li>" for x in data.why_lines(m, g))
                + f'</ul><div style="margin-top:6px;color:{T.MUTED};font-size:0.82rem">{g["tier_reason"]}</div></div>',
                unsafe_allow_html=True)
with c2:
    gaps = data.gap_lines(g)
    r = g["recent"]
    st.markdown(
        '<div class="vs-label">Evidence and gaps</div><div class="vs-body">' + data.coverage_sentence(m, g)
        + ("<ul>" + "".join(f"<li>{x}</li>" for x in gaps) + "</ul>" if gaps else " No gaps.")
        + f'<div style="margin-top:6px"><strong>{g["recent_year"]} only:</strong> {r["numeric_scored"]} numeric DO/BOD/pH readings, '
        + f"{r['exceedances']} outside the limit" + (f", lowest DO {r['min_do']:g} mg/l" if r["min_do"] is not None else "") + ".</div>"
        + f'<div style="margin-top:6px;color:{T.MUTED};font-size:0.82rem">Missing is missing, never clean.</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(f'<div class="vs-reco"><div class="t">Recommended next action · a recommendation, not a finding or order</div>'
                f'{data.recommendation(m, g)}<div style="margin-top:6px;font-size:0.78rem;color:{T.MUTED}">'
                "The decision rests with the responsible authority. Historical readings cannot describe the water today.</div></div>",
                unsafe_allow_html=True)
l1, l2, _ = st.columns([1, 1, 2])
l1.page_link("views/analysis.py", label="Readings by year and phase", icon=":material/show_chart:")
l2.page_link("views/evidence.py", label="Every reading with its page", icon=":material/fact_check:")
