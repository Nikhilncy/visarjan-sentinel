"""Page 1: the landing screen. Key metrics, the leading priority, one comparison chart, key limitations."""

import streamlit as st

from visarjan_sentinel.config import CONTEXT
from visarjan_sentinel.ui import charts, data, state
from visarjan_sentinel.ui import theme as T

m = data.get_model()
site = state.selected_site(m)
exc, num = m.totals
top = m.ghats[0]

T.page_header("Water Quality Overview", "Historical evidence, ghat priorities, and data confidence.")
st.markdown(f'<div class="vs-indicator"><span class="dot"></span>Historical MPPCB measurements, {m.period}. '
            f"The dataset ends in {m.last_year}; it does not describe the water today.</div>", unsafe_allow_html=True)

# B. main visual insight: the leading priority from the existing ranking
why = data.why_lines(m, top)[:2]
c = top["coverage"]
st.markdown(
    f'<div class="vs-feature"><div class="k">Highest priority · rank {top["rank"]} of {len(m.sites)}</div>'
    f'<div class="n">{top["site"]} {data.badges_for(m, top, include_green=False)}</div>'
    f'<div class="vs-body"><ul>{"".join(f"<li>{w}</li>" for w in why)}</ul></div>'
    f'<div class="ev">Evidence: {top["exceedances"]} of {top["numeric_scored"]} scored readings outside the applicable limits · '
    f'{c["sampled"]} of {c["expected"]} expected readings exist ({c["sampled_share"]:.0%}) · '
    f'{", ".join(data.gap_lines(top)) or "no gaps"}.</div></div>',
    unsafe_allow_html=True,
)
l1, l2, _ = st.columns([2, 2, 3], vertical_alignment="center")
l1.page_link("views/priorities.py", label="Inspect the supporting evidence", icon=":material/arrow_forward:")
l2.page_link("views/evidence.py", label="Every reading with its page", icon=":material/fact_check:")

# C. four compact metrics, each with what it counts
st.markdown(
    '<div class="vs-metrics" style="margin-top:24px">'
    f'<div><div class="q">Ghats assessed</div><div class="a">{len(m.sites)}</div>'
    f'<div class="d">Bhopal immersion ghats with MPPCB tables, {len(m.events)} festival events, {m.period}.</div></div>'
    f'<div><div class="q">Historical readings analysed</div><div class="a">{m.validation["csv_rows"]:,}</div>'
    f'<div class="d">Readings printed in the reports, all 13 tests. {m.validation["grid_cells"]:,} were expected; the gap is missing evidence.</div></div>'
    f'<div><div class="q">Readings outside DO, BOD, pH benchmarks</div><div class="a">{exc} of {num}</div>'
    f'<div class="d">Numeric DO, BOD and pH readings outside CPCB Class B: DO at least {m.do_lim:g} mg/l, BOD at most {m.bod_lim:g} mg/l, pH 6.5 to 8.5.</div></div>'
    f'<div><div class="q">Ghats with incomplete evidence</div><div class="a">{m.n_incomplete} of {len(m.sites)}</div>'
    '<div class="d">At least one expected reading not sampled or a whole festival table absent. Missing is never clean.</div></div>'
    "</div>",
    unsafe_allow_html=True,
)

# D. main comparison chart
T.section("Ghats compared, in priority order",
          f"Each bar is one ghat's numeric DO, BOD and pH readings from {m.period}, coloured by how they compare with the "
          "Class B benchmarks. The count outside the limit and its denominator are written on each bar. Click a bar to "
          "choose a ghat; hover for details.")
T.legend([(T.CAT_CRIT, T.RED), (T.CAT_OUT, T.AMBER), (T.CAT_IN, T.TEAL)], "Red in a bar means Tier 1 priority.")
st.altair_chart(charts.queue_chart(m, site), width="stretch", key="ov_queue",
                on_select=state.chart_select_callback(m, "ov_queue"), selection_mode=["ghat_sel"])
st.page_link("views/priorities.py", label="Open the full priority queue", icon=":material/arrow_forward:")

# E. key findings and limitations
T.section("Key findings and limitations")
absent = [g for g in m.ghats if g["coverage"]["absent_table"]]
rani = [g for g in m.ghats if g["site_match_confidence"] != "high"]
zero_sites = [g for g in m.ghats if g["zero_do_count"]]
finding = (f"<strong>{top['site']}</strong> recorded dissolved oxygen of <strong>0 mg/l</strong> {top['zero_do_count']} times "
           f"({data._zero_do_citations(top, 'en')}), water with no oxygen for fish life. Across all ghats, "
           f"<strong>{exc} of {num}</strong> DO, BOD and pH readings fell outside the Class B benchmarks."
           if zero_sites else f"Across all ghats, <strong>{exc} of {num}</strong> DO, BOD and pH readings fell outside the Class B benchmarks.")
warning = (f"<strong>{' and '.join(data.short(g['site']) for g in absent)}</strong> have no table at all for "
           f"{', '.join(sorted({e['festival'] + ' ' + str(e['year']) for g in absent for e in g['events'] if not e['table_present']}))}, "
           "and were sampled only during immersion in Ganesh 2025. Their most recent evidence is thin: a gap is unknown water, not clean water."
           if absent else "Every ghat has a table for every festival event.")
st.markdown(
    '<div class="vs-findings">'
    f'<div><div class="k">Most important finding</div>{finding}</div>'
    f'<div><div class="k">Missing-data warning</div>{warning}</div>'
    f'<div><div class="k">What these readings cannot tell you</div>Total coliform, also a Class B requirement, was never tested, '
    "so DO, BOD and pH alone cannot establish full Class B compliance. One sample per phase, no sampling dates, units assumed. "
    f"All readings are from {m.period}; none describes present-day safety."
    + (f" <strong>{data.short(rani[0]['site'])}</strong> is a medium-confidence site match that may cover two places." if rani else "")
    + "</div></div>",
    unsafe_allow_html=True,
)
st.page_link("views/evidence.py", label="See the source evidence and data gaps", icon=":material/arrow_forward:")

T.section("Officer brief", "A short, forwardable briefing generated today from the validated figures. Preview it in either language.")
b1, b2, _ = st.columns([1, 1, 2])
if b1.button("Preview English brief", width="stretch", type="primary"):
    state.set_brief_lang("en")
    st.switch_page("views/brief.py")
if b2.button("Preview Hindi brief · हिंदी", width="stretch"):
    state.set_brief_lang("hi")
    st.switch_page("views/brief.py")

st.markdown(
    f'<div class="vs-footer">Planning context from settings.toml: {CONTEXT.organisation}, {CONTEXT.event_name} on '
    f"{CONTEXT.event_date_en}. Data: {CONTEXT.source_label}, {m.period}. No live government system is connected.</div>",
    unsafe_allow_html=True,
)
