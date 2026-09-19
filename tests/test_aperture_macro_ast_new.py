from math import isinf

import pytest

from photonx_eda_pcb.aperture_macros import evaluate_macro, parse_macro_body
from photonx_eda_pcb.aperture_macros.ast import MacroPrimitive
from photonx_eda_pcb.aperture_macros.expression import eval_expr
from photonx_eda_pcb.aperture_macros.primitives import SUPPORTED
from photonx_eda_pcb.aperture_macros.validation import validate_macro


def test_macro_ast_and_eval():
    primitives = parse_macro_body("1,1,2.0,0,0*20,1,0.2,-1,0,1,0*")
    result = evaluate_macro(primitives)
    assert result[0]["kind"] == "circle"
    assert result[0]["values"][1] == 2.0


def test_macro_expression_is_restricted():
    assert eval_expr("2+3x4") == 14
    with pytest.raises(ValueError):
        eval_expr("__import__('os')")


@pytest.mark.parametrize("expression", ["1e309", "1e308x1e308"])
def test_macro_expression_rejects_non_finite_values(expression):
    with pytest.raises(ValueError, match="non-finite macro expression"):
        eval_expr(expression)


def test_macro_evaluator_rejects_non_finite_ad_parameters():
    primitives = parse_macro_body("1,1,$1,0,0*")
    with pytest.raises(ValueError, match=r"macro variable \$1 must be finite"):
        evaluate_macro(primitives, {"1": "1e309"})


def test_macro_evaluator_rejects_overflowing_variable_definition():
    primitives = parse_macro_body("$2=1e308x1e308*1,1,$2,0,0*")
    with pytest.raises(ValueError, match="non-finite macro expression"):
        evaluate_macro(primitives)


def test_macro_validation_tracks_registered_primitive_set():
    for code in SUPPORTED:
        issues = validate_macro([MacroPrimitive(code, ("1",))])
        assert not any(issue[1] == "MACRO_PRIMITIVE_UNSUPPORTED" for issue in issues)


def test_macro_validation_still_flags_unknown_primitives():
    issues = validate_macro([MacroPrimitive(999, ("1",))])
    assert ("warning", "MACRO_PRIMITIVE_UNSUPPORTED", 0, 999) in issues



def test_macro_evaluator_can_defer_non_finite_validation():
    primitives = parse_macro_body("1,1,$1,0,0*")
    result = evaluate_macro(
        primitives,
        {"1": "1e309"},
        reject_nonfinite=False,
    )
    assert isinf(result[0]["values"][1])
