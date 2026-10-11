from visarjan_sentinel.loader import ABSENT_TABLE, BDL, NOT_SAMPLED, NUMERIC, Event, Reading
from visarjan_sentinel.rules import EXCEEDS, MISSING, NO_LIMIT, STATUS_BDL, WITHIN, status_of


def test_class_b_limits_come_from_the_csv(limits):
    assert limits.water_class == "B"
    assert "bathing" in limits.designated_use.lower()
    assert set(limits.limits) == {"pH", "Dissolved oxygen", "BOD"}
    do, bod, ph = limits.limits["Dissolved oxygen"], limits.limits["BOD"], limits.limits["pH"]
    assert (do.limit_type, do.low) == ("min", 5.0)
    assert (bod.limit_type, bod.high) == ("max", 3.0)
    assert (ph.limit_type, ph.low, ph.high) == ("range", 6.5, 8.5)


def test_coliform_is_disclosed_as_untested(limits):
    assert limits.untested == ["Total coliform"]


def _reading(parameter, state, value=None, flag=""):
    return Reading(Event(2025, "Ganesh"), "X", "Y", "during", parameter, state, value, "mg/l", flag,
                   "" if value is None else str(value), parameter, "X", "high", 1)


def test_status_boundaries(limits):
    assert status_of(_reading("Dissolved oxygen", NUMERIC, 5.0), limits) == WITHIN
    assert status_of(_reading("Dissolved oxygen", NUMERIC, 4.99), limits) == EXCEEDS
    assert status_of(_reading("Dissolved oxygen", NUMERIC, 0.0), limits) == EXCEEDS
    assert status_of(_reading("BOD", NUMERIC, 3.0), limits) == WITHIN
    assert status_of(_reading("BOD", NUMERIC, 3.1), limits) == EXCEEDS
    assert status_of(_reading("pH", NUMERIC, 6.5), limits) == WITHIN
    assert status_of(_reading("pH", NUMERIC, 8.5), limits) == WITHIN
    assert status_of(_reading("pH", NUMERIC, 6.49), limits) == EXCEEDS
    assert status_of(_reading("pH", NUMERIC, 9.2), limits) == EXCEEDS


def test_missing_and_bdl_are_never_within(limits):
    assert status_of(_reading("Dissolved oxygen", NOT_SAMPLED), limits) == MISSING
    assert status_of(_reading("Dissolved oxygen", ABSENT_TABLE), limits) == MISSING
    assert status_of(_reading("BOD", BDL, flag="BDL"), limits) == STATUS_BDL
    # a BDL metal has no Class B limit, so it is "no limit", and its BDL state is kept on the reading itself
    assert status_of(_reading("Lead", BDL, flag="BDL"), limits) == NO_LIMIT


def test_parameters_without_class_b_limit_are_not_scored(limits):
    for p in ("COD", "Total solids", "Dissolved solids", "Suspended solids", "Turbidity",
              "Conductivity", "Chromium", "Lead", "Zinc", "Copper"):
        assert status_of(_reading(p, NUMERIC, 999.0), limits) == NO_LIMIT


def test_headline_counts_from_problem_statement(grid, limits):
    do = [r for r in grid.readings if r.parameter == "Dissolved oxygen" and r.state == NUMERIC]
    bod = [r for r in grid.readings if r.parameter == "BOD" and r.state == NUMERIC]
    ph = [r for r in grid.readings if r.parameter == "pH" and r.state == NUMERIC]
    assert (sum(status_of(r, limits) == EXCEEDS for r in do), len(do)) == (42, 116)
    assert (sum(status_of(r, limits) == EXCEEDS for r in bod), len(bod)) == (100, 112)
    assert (sum(status_of(r, limits) == EXCEEDS for r in ph), len(ph)) == (6, 115)
