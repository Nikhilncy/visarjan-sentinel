import datetime as dt
import re

import pytest

from visarjan_sentinel import build
from visarjan_sentinel.brief import render_brief, write_briefs

DATE = dt.date(2026, 10, 11)


@pytest.fixture(scope="module")
def ranking(tmp_path_factory):
    out = tmp_path_factory.mktemp("outputs")
    return build.run(out_dir=out)["ranking"]


@pytest.fixture(scope="module")
def en(ranking):
    return render_brief(ranking, "en", DATE)


@pytest.fixture(scope="module")
def hi(ranking):
    return render_brief(ranking, "hi", DATE)


def test_briefs_are_deterministic(ranking, en, hi):
    assert render_brief(ranking, "en", DATE) == en
    assert render_brief(ranking, "hi", DATE) == hi


def test_generation_date_present(en, hi):
    assert "11 October 2026" in en
    assert "11 अक्टूबर 2026" in hi


def test_required_sections_english(en):
    for heading in ("Highest follow-up priority", "Full ranking", "Key evidence",
                    "Recommended follow-up actions", "Data gaps and limitations", "Statement", "Sources"):
        assert heading in en
    assert "recommendations for the officer's consideration, not findings" in en
    assert "Historical data cannot determine current water safety" in en
    assert "Total coliform" in en or "total coliform" in en


def test_required_sections_hindi(hi):
    for heading in ("सर्वोच्च अनुवर्ती प्राथमिकता", "पूर्ण क्रम", "मुख्य साक्ष्य",
                    "अनुशंसित अनुवर्ती कार्रवाई", "आँकड़ों की कमियाँ और सीमाएँ", "स्पष्ट कथन", "स्रोत"):
        assert heading in hi
    assert "अनुशंसाएँ हैं, निष्कर्ष नहीं" in hi
    assert "ऐतिहासिक आँकड़ों से वर्तमान जल-सुरक्षा का निर्धारण नहीं किया जा सकता" in hi
    assert "total coliform" in hi


def test_tier1_ghats_and_citations(ranking, en, hi):
    tier1 = [g for g in ranking["ghats"] if g["tier"] == 1]
    assert tier1, "fixture data should have tier 1 ghats"
    for g in tier1:
        for text in (en, hi):
            assert f"Rank {g['rank']}: {g['site']}" in text or f"क्रम {g['rank']}: {g['site']}" in text
            assert g["min_do_citation"] in text  # report title + page, untranslated
    assert "0 mg/l 4 times (2023 report p.26, p.60; 2025 report p.28)" in en
    assert "4 बार 0 mg/l (2023 रिपोर्ट p.26, p.60; 2025 रिपोर्ट p.28)" in hi


def test_full_ranking_table_matches_ranking(ranking, en, hi):
    for g in ranking["ghats"]:
        assert f"| {g['rank']} | {g['tier']} | {g['site']} | {g['exceedances']} of {g['numeric_scored']} |" in en
        assert f"| {g['rank']} | {g['tier']} | {g['site']} | {g['numeric_scored']} में से {g['exceedances']} |" in hi


def test_site_names_units_and_pages_not_translated(ranking, hi):
    for g in ranking["ghats"]:
        assert g["site"] in hi
    assert "mg/l" in hi and "µS/cm" in hi and "NTU" in hi
    assert re.search(r"page \d+", hi), "citations keep the English report title and page"


def test_no_python_none_or_placeholder_leaks(en, hi):
    for text in (en, hi):
        assert "None" not in text
        assert "{" not in text and "}" not in text


def test_rani_kamlapati_caveat_in_both(en, hi):
    assert "MEDIUM confidence" in en
    assert "मध्यम (MEDIUM)" in hi


def test_missing_data_is_called_missing_not_clean(en, hi):
    assert "Unsampled, not clean" in en
    assert "स्वच्छ नहीं" in hi


def test_unknown_language_rejected(ranking):
    with pytest.raises(ValueError):
        render_brief(ranking, "fr", DATE)


def test_write_briefs(ranking, tmp_path):
    paths = write_briefs(ranking, tmp_path, DATE)
    assert paths["en"].read_text(encoding="utf-8").startswith("# Visarjan Sentinel")
    assert paths["hi"].read_text(encoding="utf-8").startswith("# विसर्जन सेंटिनल")
