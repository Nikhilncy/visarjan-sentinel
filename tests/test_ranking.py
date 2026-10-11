import pytest

from visarjan_sentinel.loader import Event
from visarjan_sentinel.ranking import rank_ghats

BAIRAGARH = "Bairagarh (Sant Hirdaram) kund"
MALIKHEDI = "Malikhedi kund"
RANI = "Rani Kamlapati ghat / Kamla Park kund"


@pytest.fixture(scope="module")
def scores(grid, limits):
    return rank_ghats(grid, limits)


def test_seven_ghats_ranked_once(scores):
    assert [g.rank for g in scores] == list(range(1, 8))
    assert len({g.site for g in scores}) == 7


def test_share_is_exceedances_over_numeric_only(scores):
    for g in scores:
        assert g.numeric_scored == sum(t.numeric for t in g.per_parameter.values())
        assert g.exceedances == sum(t.exceedances for t in g.per_parameter.values())
        assert g.exceedance_share == pytest.approx(g.exceedances / g.numeric_scored)
        # missing cells are counted in coverage, never in the score denominator
        assert g.scored_coverage.expected >= g.numeric_scored + g.scored_coverage.not_sampled + g.scored_coverage.absent_table


def test_tier_one_is_exactly_the_ghats_with_do_below_2(scores):
    tier1 = {g.site for g in scores if g.tier == 1}
    assert tier1 == {BAIRAGARH, MALIKHEDI}
    assert all(g.min_do < 2 for g in scores if g.tier == 1)
    assert all(g.min_do >= 2 for g in scores if g.tier == 2)
    # tiers are contiguous at the top of the list
    assert [g.tier for g in scores] == sorted(g.tier for g in scores)


def test_bairagarh_is_first_with_four_zero_readings(scores):
    top = scores[0]
    assert top.site == BAIRAGARH
    assert top.zero_do_count == 4
    assert top.min_do == 0.0
    assert top.per_parameter["Dissolved oxygen"].exceedances == 11
    assert top.per_parameter["Dissolved oxygen"].numeric == 13
    assert top.per_parameter["BOD"].exceedances == 13
    assert "0 mg/l 4 times" in top.reason
    assert "p.26" in top.reason and "p.60" in top.reason and "p.28" in top.reason


def test_order_within_tier_is_share_then_min_do(scores):
    for a, b in zip(scores, scores[1:]):
        if a.tier == b.tier:
            assert a.exceedance_share >= b.exceedance_share
            if a.exceedance_share == b.exceedance_share:
                assert a.min_do <= b.min_do


def test_hand_computed_shares(scores):
    by = {g.site: g for g in scores}
    assert (by[BAIRAGARH].exceedances, by[BAIRAGARH].numeric_scored) == (24, 39)
    assert (by[MALIKHEDI].exceedances, by[MALIKHEDI].numeric_scored) == (20, 39)
    assert (by["Hathaikheda dam / kund"].exceedances, by["Hathaikheda dam / kund"].numeric_scored) == (19, 54)
    assert (by["Prempura ghat"].exceedances, by["Prempura ghat"].numeric_scored) == (14, 50)  # DO 3 + BOD 9 + pH 2


def test_coverage_shows_gaps_without_changing_score(scores):
    by = {g.site: g for g in scores}
    b = by[BAIRAGARH]
    assert b.coverage.expected == 228
    assert b.coverage.absent_table == 36
    assert b.coverage.not_sampled == 26
    assert b.coverage.sampled_share < 0.75
    full = by["Khatlapura ghat"]
    assert full.coverage.absent_table == 0
    assert full.coverage.sampled_share > 0.95


def test_recent_window_is_separate_from_historical(scores):
    by = {g.site: g for g in scores}
    b = by[BAIRAGARH]
    assert b.recent_year == 2025
    assert b.recent.numeric_scored == 3  # during-phase DO, BOD, pH in Ganesh 2025 only
    assert b.recent.min_do == 0.0
    assert b.recent.coverage.absent_table == 36
    assert b.recent.coverage.not_sampled == 26


def test_rani_kamlapati_carries_site_match_warning(scores):
    g = next(g for g in scores if g.site == RANI)
    assert g.site_match_confidence == "medium"
    assert any("MEDIUM confidence" in w for w in g.warnings)
    assert all("MEDIUM confidence" not in w for s in scores if s.site != RANI for w in s.warnings)


def test_missing_data_warnings_present(scores):
    by = {g.site: g for g in scores}
    assert any("No Durga 2025 table" in w for w in by[BAIRAGARH].warnings)
    assert any("Ganesh 2025" in w and "not sampled" in w for w in by[MALIKHEDI].warnings)
    assert "Data gaps" in by[MALIKHEDI].reason


def test_event_summaries_cite_pages(scores):
    g = next(g for g in scores if g.site == BAIRAGARH)
    ev = {(e.year, e.festival): e for e in g.events}
    assert ev[(2023, "Durga")].pages == [60]
    assert ev[(2023, "Durga")].do_by_phase == {"pre": "0", "during": "0", "after": "4.2"}
    assert ev[(2025, "Durga")].table_present is False
    assert ev[(2025, "Ganesh")].do_by_phase == {"pre": "not sampled", "during": "0", "after": "not sampled"}
