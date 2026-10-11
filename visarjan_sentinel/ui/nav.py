"""Navigation shell.

Landing page: a tinted horizontal menu, centred at the top, no sidebar.
Every other page: a vertical sidebar menu (active item highlighted) AND a slim page bar
with Back, a Home › Page breadcrumb and Previous / Next steps, so navigation never
depends on the sidebar being open. Streamlit's own navigation is registered hidden;
all links use st.page_link or st.switch_page, which switch pages without a reload.
"""

from __future__ import annotations

import streamlit as st

HOME = "Home"
HISTORY_KEY = "nav_history"
SHORT_LABELS = {"Ghat Priorities": "Priorities", "Historical Analysis": "Analysis",
                "Evidence & Data Gaps": "Evidence", "Officer Brief": "Brief"}


def page_slug(page) -> str:
    return (page.url_path or "").strip("/") or "home"


def record_visit(slug: str) -> None:
    """Keep an ordered history of visited pages for the Back button."""
    hist: list[str] = st.session_state.setdefault(HISTORY_KEY, [])
    if not hist or hist[-1] != slug:
        hist.append(slug)
        del hist[:-20]


def previous_slug() -> str | None:
    hist = st.session_state.get(HISTORY_KEY, [])
    return hist[-2] if len(hist) >= 2 else None


TOP_MENU_SLUGS = ("overview", "priorities", "brief")  # the landing menu shows only the primary destinations


def top_menu(pages: list) -> None:
    """Horizontal, centred, tinted menu for the landing page: the three primary destinations."""
    shown = [p for p in pages if page_slug(p) in TOP_MENU_SLUGS]
    with st.container(key="topnav"):
        cols = st.columns(len(shown), gap="small")
        for col, page in zip(cols, shown):
            with col:
                with st.container(key=f"top_{page_slug(page)}"):
                    st.page_link(page, label=page.title, icon=page.icon, width="stretch", help=page.title)


def left_rail(pages: list, status_html: str, brand_svg: str) -> None:
    """Vertical navy menu built into the page layout (not the Streamlit sidebar), so it is always visible.
    The active item is highlighted by active_css(); the rail slides in when arriving from the landing page."""
    with st.container(key="leftnav"):
        st.markdown(f'<div class="vs-rail-brand">{brand_svg}</div>', unsafe_allow_html=True)
        for page in pages:
            with st.container(key=f"nav_{page_slug(page)}"):
                st.page_link(page, label=page.title, icon=page.icon, width="stretch")
        st.markdown('<div class="vs-side-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="vs-side-note">{status_html}</div>', unsafe_allow_html=True)


def page_bar(home, pages: list, current) -> None:
    """Back · Home › Page · Previous / Next. Rendered at the top of every inner page."""
    by_slug = {page_slug(p): p for p in [home] + pages}
    idx = next(i for i, p in enumerate(pages) if page_slug(p) == page_slug(current))
    prev_page = pages[idx - 1] if idx > 0 else home
    next_page = pages[idx + 1] if idx + 1 < len(pages) else None
    back_slug = previous_slug()

    with st.container(key="pagebar"):
        c_back, c_crumb, c_prev, c_next = st.columns([1.4, 3.6, 1.6, 1.6], vertical_alignment="center")
        with c_back:
            if st.button("Back", icon=":material/arrow_back:", key="btn_back", width="stretch",
                         help="Return to the page you came from"):
                target = by_slug.get(back_slug, home)
                hist = st.session_state.get(HISTORY_KEY, [])
                if len(hist) >= 2:
                    del hist[-2:]  # leaving current and arriving at the previous page re-records it
                st.switch_page(target)
        with c_crumb:
            st.markdown(
                f'<div class="vs-crumb"><a href="/" target="_self">Home</a><span class="sep">›</span>'
                f'<span class="cur">{current.title}</span>'
                f'<span class="step">Step {idx + 1} of {len(pages)}</span></div>',
                unsafe_allow_html=True,
            )
        with c_prev:
            with st.container(key="pb_prev"):
                st.page_link(prev_page, label=f"{SHORT_LABELS.get(prev_page.title, prev_page.title)}",
                             icon=":material/chevron_left:", width="stretch", help=f"Previous: {prev_page.title}")
        with c_next:
            with st.container(key="pb_next"):
                if next_page is not None:
                    st.page_link(next_page, label=f"{SHORT_LABELS.get(next_page.title, next_page.title)}",
                                 icon=":material/chevron_right:", width="stretch", help=f"Next: {next_page.title}")
                else:
                    st.page_link(home, label="Home", icon=":material/home:", width="stretch", help="Back to the landing page")


def active_css(current_slug: str, on_home: bool) -> str:
    """Per-run CSS: highlight the active sidebar link; hide the sidebar only on the landing page."""
    css = f"""
<style>
.st-key-nav_{current_slug} [data-testid="stPageLink"] a {{ background: rgba(255,255,255,0.16); }}
.st-key-nav_{current_slug} [data-testid="stPageLink"] a span, .st-key-nav_{current_slug} [data-testid="stPageLink"] a p {{ color: #FFFFFF; }}
</style>"""
    if on_home:
        css += """
<style>
.block-container { max-width: 1120px; padding-top: 2rem; }
</style>"""
    else:
        css += """
<style>
.block-container { max-width: 1400px; padding-top: 1.25rem; }
</style>"""
    return css
