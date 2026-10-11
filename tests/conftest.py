import pytest

from visarjan_sentinel.loader import build_grid, load_readings, validate
from visarjan_sentinel.rules import load_limits
from visarjan_sentinel.sources import CPCB_CSV, READINGS_CSV


@pytest.fixture(scope="session")
def readings():
    return load_readings(READINGS_CSV)


@pytest.fixture(scope="session")
def grid(readings):
    return build_grid(readings)


@pytest.fixture(scope="session")
def report(readings, grid):
    return validate(readings, grid)


@pytest.fixture(scope="session")
def limits():
    return load_limits(CPCB_CSV)
