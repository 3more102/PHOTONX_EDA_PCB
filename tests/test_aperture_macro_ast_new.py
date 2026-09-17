import pytest
from photonx_eda_pcb.aperture_macros import parse_macro_body,evaluate_macro
from photonx_eda_pcb.aperture_macros.expression import eval_expr
def test_macro_ast_and_eval():
    primitives=parse_macro_body("1,1,2.0,0,0*20,1,0.2,-1,0,1,0*")
    result=evaluate_macro(primitives)
    assert result[0]["kind"]=="circle" and result[0]["values"][1]==2.0
def test_macro_expression_is_restricted():
    assert eval_expr("2+3x4")==14
    with pytest.raises(ValueError): eval_expr("__import__('os')")
