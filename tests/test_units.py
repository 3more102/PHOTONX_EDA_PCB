import pytest
from photonx_eda_pcb.units import CoordinateFormat, to_mm


def test_leading_zero_coordinate_decode(): assert CoordinateFormat(2, 4, "L").decode("80000") == pytest.approx(8.0)
def test_trailing_zero_coordinate_decode(): assert CoordinateFormat(2, 4, "T").decode("8") == pytest.approx(80.0)
def test_inch_conversion(): assert to_mm(1.0, "inch") == pytest.approx(25.4)
