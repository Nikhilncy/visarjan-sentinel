"""Landing page: what Visarjan Sentinel is and where to go. No data tables here."""

import streamlit as st

from visarjan_sentinel.config import CONTEXT
from visarjan_sentinel.ui import data
from visarjan_sentinel.ui import theme as T

m = data.get_model()
exc, num = m.totals
top = m.ghats[0]

WAVES = (
    '<svg class="vs-waves" viewBox="0 0 1200 140" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path class="w1" d="M0 70 C 150 20, 300 120, 450 70 S 750 20, 900 70 S 1150 120, 1200 70 S 1500 20, 1650 70 S 1950 120, 2100 70 S 2350 20, 2400 70 V140 H0 Z" fill="#2563EB" fill-opacity="0.10"/>'
    '<path class="w2" d="M0 90 C 200 40, 400 140, 600 90 S 1000 40, 1200 90 S 1600 140, 1800 90 S 2200 40, 2400 90 V140 H0 Z" fill="#0D9488" fill-opacity="0.12"/>'
    '<path class="w3" d="M0 110 C 250 70, 450 150, 700 110 S 1050 70, 1200 110 S 1450 150, 1700 110 S 2050 70, 2400 110 V140 H0 Z" fill="#142B4A" fill-opacity="0.10"/>'
    "</svg>"
    '<span class="vs-ripple r1"></span><span class="vs-ripple r2"></span><span class="vs-ripple r3"></span>'
)
DROP = ('<svg width="40" height="40" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        '<path d="M17 5c-4.4 6-7.6 10.3-7.6 14.2a7.6 7.6 0 0 0 15.2 0C24.6 15.3 21.4 11 17 5z" fill="{fill}" fill-opacity="{op}"/>'
        '<path d="M13.2 20.4a3.9 3.9 0 0 0 3.8 3.9" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="1.6" stroke-linecap="round"/>'
        "</svg>")

st.markdown(
    f'<div class="vs-hero">{WAVES}<div class="in">'
    f'<div class="eyebrow reveal r0"><span class="mark">{T.MARK_SVG}</span>{T.DESCRIPTOR}</div>'
    f'<h1 class="title reveal r1">{T.PRODUCT}</h1>'
    "<p class=\"sub reveal r2\">Turns three years of buried immersion-ghat water tests into a ranked, traceable follow-up list "
    "for the municipal officer: which ghats need attention first, why, how complete the evidence is, and what to do next.</p>"
    f'<div class="facts reveal r3"><span><strong>{len(m.sites)}</strong> Bhopal ghats</span>'
    f'<span><strong>{m.validation["csv_rows"]:,}</strong> readings, {m.period}</span>'
    f'<span><strong>{exc} of {num}</strong> readings outside Class B limits</span>'
    f'<span><strong>{len(m.tier1)}</strong> ghats in priority tier 1</span></div>'
    "</div></div>",
    unsafe_allow_html=True,
)

b1, b2, _ = st.columns([1.3, 1.3, 3], vertical_alignment="center")
if b1.button("Open the overview", type="primary", width="stretch"):
    st.switch_page("views/overview.py")
if b2.button("See ghat priorities", width="stretch"):
    st.switch_page("views/priorities.py")

T.section("What you can do here")
tiles = [
    (DROP.format(fill=T.RED, op="0.9"), "Which ghats need attention first",
     f"A ranked queue of all {len(m.sites)} ghats. Tier 1 means dissolved oxygen was recorded below 2 mg/l, water with "
     "almost no oxygen for fish life.", "views/priorities.py", "Ghat Priorities"),
    (DROP.format(fill=T.AMBER, op="0.9"), "Why each ghat is prioritised",
     "Every reading compared with the CPCB Class B bathing-water benchmarks, by year and sampling phase, in plain language.",
     "views/analysis.py", "Historical Analysis"),
    (DROP.format(fill=T.GREY_DARK, op="0.9"), "How complete the evidence is",
     "Which samples exist, which are missing, and the exact MPPCB report page behind every number. Missing is never clean.",
     "views/evidence.py", "Evidence & Data Gaps"),
    (DROP.format(fill=T.TEAL, op="0.9"), "What to do next",
     "A recommendation per ghat and a forwardable brief in English and Hindi, generated on the day from the validated figures.",
     "views/brief.py", "Officer Brief"),
]
cols = st.columns(4, gap="medium")
for col, (icon, head, body, target, label) in zip(cols, tiles):
    with col:
        st.markdown(f'<div class="vs-tile reveal"><div class="ic">{icon}</div><div class="h">{head}</div><div class="b">{body}</div></div>',
                    unsafe_allow_html=True)
        st.page_link(target, label=label, icon=":material/arrow_forward:")

T.section("How the evidence is read")
st.markdown(
    '<div class="vs-findings">'
    f'<div><div class="k">Benchmarks</div>CPCB Class B, outdoor bathing: dissolved oxygen at least <strong>{m.do_lim:g} mg/l</strong>, '
    f"BOD at most <strong>{m.bod_lim:g} mg/l</strong>, pH <strong>6.5 to 8.5</strong>. Limits come from the CPCB criteria file; "
    "nothing is invented for other tests. Total coliform was never tested, so full Class B compliance cannot be assessed.</div>"
    f'<div><div class="k">Historical, not current</div>All readings are MPPCB measurements from {m.period}. The dataset ends in '
    f"{m.last_year} and does not describe the water today. The tool shows where problems have been recorded so fresh sampling and "
    "cleaning can be sent there first.</div>"
    '<div><div class="k">Missing is missing</div>A blank cell is <strong>not sampled</strong>, a missing table is <strong>absent</strong>, '
    "a metal printed BDL is <strong>below detection limit</strong>. None of these is treated as clean, and evidence coverage is shown "
    "beside the ranking, never inside it.</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="vs-footer">Built for {CONTEXT.organisation}. Data: {CONTEXT.source_label}, {m.period}. Open source, MIT licence. '
    "No live government system is connected.</div>",
    unsafe_allow_html=True,
)
