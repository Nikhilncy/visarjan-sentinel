"""Page 5: preview and share the officer brief in English or Hindi."""

import streamlit as st

from visarjan_sentinel.brief import render_brief
from visarjan_sentinel.config import CONTEXT
from visarjan_sentinel.ui import data, state
from visarjan_sentinel.ui import theme as T

m = data.get_model()
today = data.today()
lang = state.brief_lang()

T.page_header("Officer Brief", "A concise briefing an officer can forward. Choose the language, preview it, then download.")

names = state.LANGS
choice = st.radio("Language", options=list(names), index=list(names).index(lang), format_func=lambda k: names[k],
                  horizontal=True, key="brief_lang_widget", on_change=lambda: state.set_brief_lang(st.session_state["brief_lang_widget"]))
lang = choice
text = render_brief(m.ranking, lang, today, CONTEXT)
lang_name = "English" if lang == "en" else "Hindi"

a1, a2, _ = st.columns([1, 1, 2], vertical_alignment="center")
a1.download_button(f"Download {lang_name} brief", data=text.encode("utf-8"),
                   file_name=f"visarjan_sentinel_brief_{lang}_{today.isoformat()}.md", mime="text/markdown",
                   width="stretch", type="primary", key=f"dl_{lang}")
show_plain = a2.toggle(f"Copy {lang_name} brief", key="brief_copy",
                       help="Shows the brief as plain text with a copy button in its top-right corner.")
st.markdown(
    f'<div class="vs-lead">Generated {today.strftime("%d %B %Y")} from the validated ranking by a fixed template; '
    f"nothing is written by a language model. Historical data {m.period}; the brief states that it does not establish "
    "current water conditions." + (" Hindi is a template draft and must be reviewed by a fluent Hindi speaker before external use."
                                   if lang == "hi" else "") + "</div>",
    unsafe_allow_html=True,
)
if show_plain:
    st.markdown('<div class="vs-lead">Use the copy icon at the top-right of the box to copy the whole brief.</div>',
                unsafe_allow_html=True)
    st.code(text, language=None, wrap_lines=True, height=320)
with st.container(border=True, key="brief_preview"):
    st.markdown(text)
