"""Pin the counts found during the data inspection so the loader cannot drift."""

from collections import Counter

from visarjan_sentinel.loader import ABSENT_TABLE, BDL, NOT_SAMPLED, NUMERIC, Event

BAIRAGARH = "Bairagarh (Sant Hirdaram) kund"
MALIKHEDI = "Malikhedi kund"


def test_csv_row_count(readings):
    assert len(readings) == 1524


def test_raw_states_match_inspection(readings):
    c = Counter(r.state for r in readings)
    assert c[NUMERIC] == 1289
    assert c[BDL] == 174
    assert c[NOT_SAMPLED] == 61  # 48 blank + 9 underscore + 4 asterisk cells


def test_zero_is_numeric_not_missing(readings):
    zeros = [r for r in readings if r.state == NUMERIC and r.value == 0]
    assert len(zeros) == 4
    assert {r.site for r in zeros} == {BAIRAGARH}
    assert {r.parameter for r in zeros} == {"Dissolved oxygen"}
    assert sorted((r.event.year, r.event.festival, r.phase, r.source_page) for r in zeros) == [
        (2023, "Durga", "during", 60),
        (2023, "Durga", "pre", 60),
        (2023, "Ganesh", "after", 26),
        (2025, "Ganesh", "during", 28),
    ]


def test_bdl_has_no_value(readings):
    assert all(r.value is None for r in readings if r.state == BDL)
    assert all(r.parameter in {"Chromium", "Lead", "Zinc", "Copper"} for r in readings if r.state == BDL)


def test_grid_dimensions(grid):
    assert len(grid.sites) == 7
    assert len(grid.events) == 6
    assert grid.events[0] == Event(2023, "Ganesh")
    assert grid.events[-1] == Event(2025, "Durga")
    # Suspended solids was printed in only four of six events.
    assert [len(grid.parameters_by_event[e]) for e in grid.events] == [13, 12, 13, 13, 13, 12]
    assert len(grid.readings) == 7 * 3 * (13 + 12 + 13 + 13 + 13 + 12)  # 1596


def test_absent_tables_are_filled_and_distinct(grid):
    absent = [r for r in grid.readings if r.state == ABSENT_TABLE]
    assert len(absent) == 2 * 12 * 3  # two missing Durga 2025 tables, 12 parameters, 3 phases
    assert {(r.site, r.event) for r in absent} == {
        (BAIRAGARH, Event(2025, "Durga")),
        (MALIKHEDI, Event(2025, "Durga")),
    }
    assert all(r.source_page is None and r.value is None for r in absent)
    assert not grid.table_present(BAIRAGARH, Event(2025, "Durga"))
    assert grid.table_present(BAIRAGARH, Event(2025, "Ganesh"))


def test_ganesh_2025_pre_and_after_not_sampled_at_two_ghats(grid):
    for site in (BAIRAGARH, MALIKHEDI):
        rows = [r for r in grid.readings if r.site == site and r.event == Event(2025, "Ganesh")]
        by_phase = Counter((r.phase, r.state) for r in rows)
        assert by_phase[("pre", NOT_SAMPLED)] == 13
        assert by_phase[("after", NOT_SAMPLED)] == 13
        assert by_phase[("during", NUMERIC)] + by_phase[("during", BDL)] == 13


def test_every_cell_has_a_citation_or_says_why(grid):
    for r in grid.readings:
        if r.state == ABSENT_TABLE:
            assert "no table" in r.citation
        else:
            assert r.source_page is not None
            assert f"page {r.source_page}" in r.citation


def test_validation_passes(report):
    assert report.ok, report.warnings
    assert report.duplicate_keys == 0
    assert report.grid_cells == 1596
    assert report.state_counts == {NUMERIC: 1289, BDL: 174, NOT_SAMPLED: 61, ABSENT_TABLE: 72}
    assert ("Rani Kamlapati ghat / Kamla Park kund" in w for w in report.warnings)
    assert any("medium" in w for w in report.warnings)
    assert len(report.absent_tables) == 2
