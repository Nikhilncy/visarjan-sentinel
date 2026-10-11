"""Visarjan Sentinel: entry point.

    streamlit run app.py

Sets up the theme, loads the validated pipeline output once, registers the pages and
draws the navigation: a horizontal menu on the landing page, a sidebar menu elsewhere.
All numbers come from visarjan_sentinel (loader, rules, ranking, brief); pages only present them.
"""

import streamlit as st

from visarjan_sentinel.ui import data, nav, state
from visarjan_sentinel.ui import theme as T

st.set_page_config(page_title=f"{T.PRODUCT} · {T.DESCRIPTOR}", page_icon="assets/mark.svg", layout="wide",
                   initial_sidebar_state="auto")
T.inject_css()

try:
    m = data.get_model()
except FileNotFoundError as exc:
    st.error(f"A required data file is missing: {exc}. Check the dataset paths in settings.toml.")
    st.stop()
except SystemExit as exc:
    st.error(f"Data validation failed, so nothing is shown. {exc}")
    st.stop()
except Exception as exc:  # noqa: BLE001
    st.error(f"The pipeline could not run: {type(exc).__name__}: {exc}")
    st.stop()

home = st.Page("views/home.py", title="Home", icon=":material/water_drop:", default=True)
pages = [
    st.Page("views/overview.py", title="Overview", icon=":material/dashboard:", url_path="overview"),
    st.Page("views/priorities.py", title="Ghat Priorities", icon=":material/format_list_numbered:", url_path="priorities"),
    st.Page("views/analysis.py", title="Historical Analysis", icon=":material/show_chart:", url_path="analysis"),
    st.Page("views/evidence.py", title="Evidence & Data Gaps", icon=":material/fact_check:", url_path="evidence"),
    st.Page("views/brief.py", title="Officer Brief", icon=":material/description:", url_path="brief"),
]
current = st.navigation([home] + pages, position="hidden")
on_home = current.title == nav.HOME
st.markdown(nav.active_css(nav.page_slug(current), on_home), unsafe_allow_html=True)

nav.record_visit(nav.page_slug(current))
if on_home:
    nav.top_menu(pages)
else:
    T.sidebar_brand()
    site = state.selected_site(m)
    nav.sidebar_menu(
        [home] + pages,
        f"<strong>Selected ghat</strong><br>{m.rank_of[site]} · {site}<br><br>"
        f"<strong>Evidence</strong><br>MPPCB immersion reports, {m.period}. Historical readings; they do not establish "
        "current water conditions.",
    )
    nav.page_bar(home, pages, current)
current.run()
