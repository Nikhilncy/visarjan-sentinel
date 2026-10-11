"""Smoke and behaviour tests for the multipage Streamlit app via AppTest."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"
PAGES = ["views/home.py", "views/overview.py", "views/priorities.py", "views/analysis.py", "views/evidence.py", "views/brief.py"]
SITES = ["Bairagarh (Sant Hirdaram) kund", "Malikhedi kund", "Khatlapura ghat",
         "Rani Kamlapati ghat / Kamla Park kund", "Shahpura lake ghat", "Hathaikheda dam / kund", "Prempura ghat"]


@pytest.fixture()
def at():
    at = AppTest.from_file(str(APP), default_timeout=120)
    at.run()
    return at


def _text(at) -> str:
    return " ".join(md.value for md in at.markdown)


def _side(at) -> str:
    return " ".join(md.value for md in at.sidebar.markdown)


def test_every_page_runs(at):
    for page in PAGES:
        at.switch_page(page).run()
        assert not at.exception, (page, [e.value for e in at.exception])


def test_landing_page_has_horizontal_menu_and_no_rail(at):
    text = _text(at)
    assert "Visarjan Sentinel" in text and "Water Quality Intelligence" in text and "vs-waves" in text
    labels = [l.label for l in at.main.get("page_link")]
    assert labels[:3] == ["Overview", "Ghat Priorities", "Officer Brief"]  # only the primary destinations
    assert '<div class="vs-rail-brand">' not in text  # no rail on the landing page (CSS may mention the class)
    assert "148 of 343" in text and "2023 to 2025" in text
    assert not at.dataframe and not at.get("vega_lite_chart")  # a clean landing page, no data tables or charts


def test_inner_pages_show_left_vertical_menu_with_home(at):
    at.switch_page("views/priorities.py").run()
    text = _text(at)
    assert '<div class="vs-rail-brand">' in text  # the rail is part of the page, not the (hidden) Streamlit sidebar
    labels = [l.label for l in at.main.get("page_link")]
    assert labels[:6] == ["Home", "Overview", "Ghat Priorities", "Historical Analysis", "Evidence & Data Gaps", "Officer Brief"]
    assert ".st-key-nav_priorities [data-testid=\"stPageLink\"] a { background" in text
    assert "Selected ghat" in text


def test_page_bar_back_breadcrumb_and_steps(at):
    at.switch_page("views/overview.py").run()
    at.switch_page("views/priorities.py").run()
    assert at.session_state["nav_history"][-2:] == ["overview", "priorities"]
    text = _text(at)
    assert 'class="vs-crumb"' in text and "Ghat Priorities" in text and "Step 2 of 5" in text
    labels = [l.label for l in at.main.get("page_link")]
    assert labels[6:8] == ["Overview", "Analysis"]  # after the six rail links: previous and next steps
    assert at.button(key="btn_back").label == "Back"
    at.switch_page("views/brief.py").run()
    labels = [l.label for l in at.main.get("page_link")]
    assert labels[6:8] == ["Evidence", "Home"]  # last step offers Home instead of Next


def test_permanent_header_has_no_event_date_or_countdown(at):
    at.switch_page("views/overview.py").run()
    text = _text(at)
    rail = text[text.index('<div class="vs-rail-brand">'):text.index('class="vs-crumb"')]
    assert "Selected ghat" in rail and "Evidence" in rail  # status area under the navigation
    assert "20 October 2026" not in rail and "days to go" not in rail
    assert "2026" not in rail and "2023 to 2025" in rail


def test_overview_landing_screen(at):
    at.switch_page("views/overview.py").run()
    text = _text(at)
    assert "# Water Quality Overview" in text
    assert "Historical evidence, ghat priorities, and data confidence." in text
    assert "Historical MPPCB measurements, 2023 to 2025" in text and "does not describe the water today" in text
    # featured leading priority from the existing ranking, with verified reasons
    assert "Highest priority · rank 1 of 7" in text and "Bairagarh (Sant Hirdaram) kund" in text
    assert "11 of 13</strong> dissolved-oxygen readings" in text and "p.26" in text
    # four explained metrics
    for q in ("Ghats assessed", "Historical readings analysed", "Readings outside DO, BOD, pH benchmarks", "Ghats with incomplete evidence"):
        assert q in text
    assert "1,524" in text and "148 of 343" in text and "4 of 7" in text
    assert "DO at least 5 mg/l, BOD at most 3 mg/l, pH 6.5 to 8.5" in text
    # one comparison chart, findings and limitations, no full ranking table
    assert len(at.get("vega_lite_chart")) == 1
    assert "Most important finding" in text and "Missing-data warning" in text
    assert "cannot establish full Class B compliance" in text
    assert 'class="vs-queue"' not in text


def test_notice_is_not_sticky(at):
    at.switch_page("views/overview.py").run()
    text = _text(at)
    assert ":has(.vs-notice)" not in text and ".vs-notice { position: sticky" not in text
    assert ".vs-indicator { position: sticky" not in text


def test_priorities_order_matches_ranking(at):
    at.switch_page("views/priorities.py").run()
    text = _text(at)
    pos = [text.index(f'<td class="nm">{s}<br>') for s in SITES]
    assert pos == sorted(pos)
    assert '<td class="num">24 of 39</td>' in text
    assert "Outside limits = numeric DO, BOD and pH readings outside the CPCB Class B" in text
    assert "Coverage never changes the rank" in text
    assert "a recommendation, not a finding or order" in text


def test_priorities_detail_follows_selection(at):
    at.switch_page("views/priorities.py").run()
    for site in SITES:
        at.session_state["selected_site"] = site
        at.session_state["ghat_pills"] = site
        at.run()
        assert not at.exception, (site, [e.value for e in at.exception])
        assert f"## {site}" in _text(at)
    at.session_state["selected_site"] = "Rani Kamlapati ghat / Kamla Park kund"
    at.session_state["ghat_pills"] = "Rani Kamlapati ghat / Kamla Park kund"
    at.run()
    assert any("MEDIUM confidence" in w.value for w in at.warning)
    at.session_state["selected_site"] = "Malikhedi kund"
    at.session_state["ghat_pills"] = "Malikhedi kund"
    at.run()
    assert any("No Durga 2025 table" in w.value and "not clean" in w.value for w in at.warning)


def test_selection_persists_across_pages(at):
    at.switch_page("views/overview.py").run()
    at.session_state["selected_site"] = "Shahpura lake ghat"
    at.switch_page("views/analysis.py").run()
    assert at.selectbox[0].value == "Shahpura lake ghat"
    at.switch_page("views/evidence.py").run()
    assert at.multiselect[0].value == ["Shahpura lake ghat"]
    assert "Selected ghat</strong><br>5 · Shahpura lake ghat" in _text(at)


def test_analysis_parameters_filters_and_benchmarks(at):
    at.switch_page("views/analysis.py").run()
    text = _text(at)
    assert "at least 5 mg/l" in text and "ranking's critical threshold, not a CPCB limit" in text
    assert len(at.get("vega_lite_chart")) == 5  # by year, three phases, all ghats compared
    assert "What this shows" in text
    for p in ("BOD", "pH"):
        at.session_state["param_select"] = p
        at.run()
        assert not at.exception, [e.value for e in at.exception]
    assert "6.5 to 8.5" in _text(at)
    # year and phase filters narrow the charts and say so
    at.session_state["years_select"] = [2024, 2025]
    at.session_state["phases_select"] = ["during"]
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.get("vega_lite_chart")) == 3  # by year, one phase, all ghats compared
    assert "Filters applied" in _text(at)


def test_evidence_browser_keeps_states_and_citations(at):
    at.switch_page("views/evidence.py").run()
    df = at.dataframe[0].value
    assert set(df["Record type"]) <= {"Numeric reading", "BDL (below detection limit)", "Not sampled", "Absent table"}
    assert {"Not sampled", "Absent table"} <= set(df["Record type"])  # Bairagarh has both
    assert "Idol_immer._Report_23_CPCB.pdf" in set(df["Report"])
    zero = df[(df["Test"] == "Dissolved oxygen") & (df["Reading"] == "0")]
    assert len(zero) == 4 and set(zero["Status"]) == {"critical (DO below 2 mg/l)"}
    assert (df[df["Record type"] == "Absent table"]["Status"] == "missing").all()
    text = _text(at)
    assert "Below detection limit" in text and "Coliform was not tested" in text
    # search narrows the records
    at.text_input(key="evidence_search").set_value("page 60").run()
    assert not at.exception
    at.text_input(key="evidence_search").set_value("Durga 2023").run()
    df = at.dataframe[0].value
    assert len(df) and set(df["Festival"]) == {"Durga"} and set(df["Year"]) == {2023}


def test_brief_copy_action_is_separate_from_download(at):
    at.switch_page("views/brief.py").run()
    labels = [b.label for b in at.get("download_button")]
    assert labels == ["Download English brief"]
    assert at.toggle(key="brief_copy").label == "Copy English brief"
    assert not at.code
    at.toggle(key="brief_copy").set_value(True).run()
    assert at.code and at.code[0].value.startswith("# Visarjan Sentinel")
    assert [b.label for b in at.get("download_button")] == ["Download English brief"]


def test_brief_language_switch_updates_preview_and_download(at):
    at.switch_page("views/brief.py").run()
    assert at.radio[0].value == "en"
    assert "# Visarjan Sentinel: Ghat follow-up brief" in _text(at)
    assert at.get("download_button")[0].label == "Download English brief"
    at.radio[0].set_value("hi").run()
    assert not at.exception
    assert "विसर्जन सेंटिनल" in _text(at)
    assert at.get("download_button")[0].label == "Download Hindi brief"
    assert at.session_state["brief_lang"] == "hi"
    assert "reviewed by a fluent Hindi speaker" in _text(at)


def test_overview_brief_buttons_set_language(at):
    at.switch_page("views/overview.py").run()
    hindi = next(b for b in at.button if "Hindi" in b.label)
    hindi.click().run()
    assert at.session_state["brief_lang"] == "hi"


def test_green_only_for_qualified_parameter(at):
    at.switch_page("views/priorities.py").run()
    at.session_state["selected_site"] = "Bairagarh (Sant Hirdaram) kund"
    at.session_state["ghat_pills"] = "Bairagarh (Sant Hirdaram) kund"
    at.run()
    assert "pH within range on every reading (this parameter only)" in _text(at)
    at.session_state["selected_site"] = "Hathaikheda dam / kund"
    at.session_state["ghat_pills"] = "Hathaikheda dam / kund"
    at.run()
    assert "pH within range on every reading" not in _text(at)
