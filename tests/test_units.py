import pytest

from photonx_eda_pcb.units import CoordinateFormat, to_mm


def test_leading_zero_coordinate_decode():
    assert CoordinateFormat(2, 4, "L").decode("80000") == pytest.approx(8.0)


def test_trailing_zero_coordinate_decode():
    assert CoordinateFormat(2, 4, "T").decode("8") == pytest.approx(80.0)


def test_explicit_decimal_coordinate_decode():
    fmt = CoordinateFormat(2, 4, "L")
    assert fmt.decode("+1.25") == pytest.approx(1.25)
    assert fmt.decode("-.5") == pytest.approx(-0.5)


def test_coordinate_width_is_enforced():
    with pytest.raises(ValueError, match="exceeds format"):
        CoordinateFormat(2, 4, "L").decode("1234567")


@pytest.mark.parametrize(
    "args",
    [
        (-1, 4, "L"),
        (2, -1, "L"),
        (0, 0, "L"),
        (2, 4, "X"),
        (True, 4, "L"),
        (2, False, "L"),
    ],
)
def test_coordinate_format_rejects_invalid_configuration(args):
    with pytest.raises(ValueError):
        CoordinateFormat(*args)


@pytest.mark.parametrize(
    "raw",
    ["", "+", "-", ".", "12.3.4", "١٢٣", "12e3", "nan", "inf", " 12"],
)
def test_coordinate_decode_rejects_malformed_tokens(raw):
    with pytest.raises(ValueError):
        CoordinateFormat(2, 4, "L").decode(raw)


def test_explicit_decimal_coordinate_must_be_finite():
    raw = "9" * 400 + ".0"
    with pytest.raises(ValueError, match="finite"):
        CoordinateFormat(2, 4, "L").decode(raw)


def test_inch_conversion():
    assert to_mm(1.0, "inch") == pytest.approx(25.4)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), True])
def test_unit_conversion_rejects_non_finite_or_boolean_values(value):
    with pytest.raises(ValueError, match="finite number"):
        to_mm(value, "mm")


def test_unit_conversion_rejects_overflow():
    with pytest.raises(ValueError, match="finite"):
        to_mm(1e308, "inch")
