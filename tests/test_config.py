import datetime as dt
from pathlib import Path

import pytest

from visarjan_sentinel import build
from visarjan_sentinel.brief import render_brief
from visarjan_sentinel.config import CONTEXT, load_context

DATE = dt.date(2026, 10, 11)


def test_default_context_loads_from_settings():
    assert CONTEXT.organisation == "Bhopal Municipal Corporation"
    assert CONTEXT.event_name == "Durga visarjan"
    assert CONTEXT.event_date == dt.date(2026, 10, 20)
    assert CONTEXT.event_date_en == "20 October 2026"
    assert CONTEXT.event_date_hi == "20 अक्टूबर 2026"
    assert sorted(CONTEXT.reports) == [2023, 2024, 2025]
    assert CONTEXT.readings_csv.exists() and CONTEXT.cpcb_csv.exists()
    assert CONTEXT.days_until_event(DATE) == 9


def test_every_data_year_has_a_report_entry(grid):
    assert {e.year for e in grid.events} <= set(CONTEXT.reports)


def _write_settings(tmp_path: Path, event_date="2027-10-09", event="Durga visarjan 2027") -> Path:
    (tmp_path / "data").mkdir()
    for name in ("bhopal_ghats_2023_2025.csv", "cpcb_water_quality_criteria.csv"):
        (tmp_path / "data" / name).write_bytes((CONTEXT.readings_csv.parent / name).read_bytes())
    p = tmp_path / "settings.toml"
    p.write_text(f'''
[organisation]
name = "Test Corporation"
name_hi = "परीक्षण निगम"
[target_event]
name = "{event}"
name_hi = "दुर्गा विसर्जन"
date = {event_date}
[dataset]
readings_csv = "data/bhopal_ghats_2023_2025.csv"
cpcb_csv = "data/cpcb_water_quality_criteria.csv"
source_label = "Test reports"
[[reports]]
year = 2023
file_name = "a.pdf"
title = "Report A"
pages = 1
url = "https://example.org/a.pdf"
[[reports]]
year = 2024
file_name = "b.pdf"
title = "Report B"
pages = 1
url = "https://example.org/b.pdf"
[[reports]]
year = 2025
file_name = "c.pdf"
title = "Report C"
pages = 1
url = "https://example.org/c.pdf"
''', encoding="utf-8")
    return p


def test_custom_context_flows_into_briefs(tmp_path):
    ctx = load_context(_write_settings(tmp_path))
    assert ctx.event_date == dt.date(2027, 10, 9)
    assert ctx.organisation_short == "Test Corporation"  # falls back to the full name
    ranking = build.run(out_dir=tmp_path / "out")["ranking"]
    en = render_brief(ranking, "en", DATE, ctx)
    hi = render_brief(ranking, "hi", DATE, ctx)
    assert "Test Corporation" in en and "9 October 2027" in en and "Durga visarjan 2027" in en
    assert "does not establish water conditions in 2027" in en
    assert "20 October 2026" not in en
    assert "परीक्षण निगम" in hi and "9 अक्टूबर 2027" in hi and "2027 की जल-स्थिति" in hi
    assert "Report A, 1 pages" in en


def test_data_years_come_from_data_not_settings(tmp_path):
    ctx = load_context(_write_settings(tmp_path))
    ranking = build.run(out_dir=tmp_path / "out")["ranking"]
    en = render_brief(ranking, "en", DATE, ctx)
    assert "historical readings from 2023 to 2025" in en
    assert "The dataset ends in 2025" in en


def test_missing_key_is_a_clear_error(tmp_path):
    p = tmp_path / "settings.toml"
    p.write_text('[organisation]\nname = "X"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="missing a required key"):
        load_context(p)
