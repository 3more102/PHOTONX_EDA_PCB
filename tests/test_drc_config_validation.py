import math

import pytest

from photonx_eda_pcb.drc.model import DrcConfig


_FIELDS = (
    "min_track_width_mm",
    "min_drill_mm",
    "min_annular_ring_mm",
    "min_clearance_mm",
    "edge_clearance_mm",
    "min_drill_copper_clearance_mm",
    "min_mechanical_copper_clearance_mm",
)


@pytest.mark.parametrize("field", _FIELDS)
@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), -1e-9])
def test_drc_config_rejects_nonfinite_and_negative_thresholds(field, value):
    with pytest.raises(ValueError, match=field):
        DrcConfig(**{field: value})


@pytest.mark.parametrize("field", _FIELDS)
def test_drc_config_accepts_zero_thresholds(field):
    cfg = DrcConfig(**{field: 0})
    value = getattr(cfg, field)
    assert value == 0.0
    assert isinstance(value, float)
    assert math.isfinite(value)


@pytest.mark.parametrize("value", ["0.15", b"0.15", True, False, None])
def test_drc_config_rejects_non_numeric_threshold_types(value):
    with pytest.raises(ValueError, match="min_clearance_mm"):
        DrcConfig(min_clearance_mm=value)
