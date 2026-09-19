import math

import pytest

from photonx_eda_pcb.footprint_reconstruction.reference_match import (
    match_reference,
    reference_candidates,
)
from photonx_eda_pcb.silkscreen_semantics.tokens import SilkToken


def test_nearer_non_reference_text_does_not_hide_reference():
    tokens = [
        SilkToken("GND", x=0.1, y=0.0),
        SilkToken("r7", x=1.0, y=0.0),
    ]
    assert match_reference(tokens, (0.0, 0.0)) == "R7"


def test_reference_candidates_keep_general_valid_designators_and_rank_deterministically():
    tokens = [
        SilkToken("Q2", x=2.0, y=0.0),
        SilkToken("L1", x=1.0, y=0.0),
        SilkToken("q2", x=1.5, y=0.0),
    ]
    assert reference_candidates(tokens, (0.0, 0.0)) == (
        ("L1", 1.0),
        ("Q2", 1.5),
    )


def test_layer_filter_prevents_cross_side_reference_assignment():
    tokens = [
        SilkToken("R1", x=0.25, y=0.0, layer="B.SilkS"),
        SilkToken("R2", x=0.50, y=0.0, layer="F.SilkS"),
    ]
    assert match_reference(tokens, (0.0, 0.0), layer="F.SilkS") == "R2"
    assert match_reference(tokens, (0.0, 0.0), layer="B.SilkS") == "R1"


def test_exact_distance_conflict_fails_closed():
    tokens = [
        SilkToken("R1", x=1.0, y=0.0),
        SilkToken("R2", x=-1.0, y=0.0),
    ]
    assert match_reference(tokens, (0.0, 0.0)) is None


def test_explicit_ambiguity_margin_rejects_near_competing_reference():
    tokens = [
        SilkToken("C1", x=1.0, y=0.0),
        SilkToken("C2", x=1.1, y=0.0),
    ]
    assert match_reference(tokens, (0.0, 0.0), ambiguity_margin_mm=0.05) == "C1"
    assert match_reference(tokens, (0.0, 0.0), ambiguity_margin_mm=0.10) is None


def test_non_finite_token_coordinate_is_ignored():
    tokens = [
        SilkToken("R1", x=math.nan, y=0.0),
        SilkToken("R2", x=2.0, y=0.0),
    ]
    assert match_reference(tokens, (0.0, 0.0)) == "R2"


@pytest.mark.parametrize(
    ("kwargs", "center"),
    [
        ({"max_distance_mm": -1.0}, (0.0, 0.0)),
        ({"ambiguity_margin_mm": -0.1}, (0.0, 0.0)),
        ({}, (math.inf, 0.0)),
    ],
)
def test_invalid_matching_configuration_is_rejected(kwargs, center):
    with pytest.raises(ValueError):
        match_reference([SilkToken("R1")], center, **kwargs)
