"""Session state shared across pages: the selected ghat and the brief language."""

from __future__ import annotations

import streamlit as st

from .data import Model

SITE_KEY = "selected_site"
LANG_KEY = "brief_lang"
LANGS = {"en": "English", "hi": "हिंदी"}


def selected_site(m: Model) -> str:
    if st.session_state.get(SITE_KEY) not in m.by_site:
        st.session_state[SITE_KEY] = m.sites[0]
    return st.session_state[SITE_KEY]


def set_site(site: str) -> None:
    st.session_state[SITE_KEY] = site
    for widget_key in ("ghat_pills", "ghat_select"):
        if widget_key in st.session_state:
            st.session_state[widget_key] = site


def chart_select_callback(m: Model, *keys: str):
    """on_select callback for charts that carry a 'ghat_sel' point selection on the site field."""
    def _cb() -> None:
        for key in keys:
            state = st.session_state.get(key)
            if state is None:
                continue
            rows = state.selection.get("ghat_sel", [])
            if rows and rows[0].get("site") in m.by_site:
                set_site(rows[0]["site"])
                return
    return _cb


def brief_lang() -> str:
    if st.session_state.get(LANG_KEY) not in LANGS:
        st.session_state[LANG_KEY] = "en"
    return st.session_state[LANG_KEY]


def set_brief_lang(lang: str) -> None:
    st.session_state[LANG_KEY] = lang
