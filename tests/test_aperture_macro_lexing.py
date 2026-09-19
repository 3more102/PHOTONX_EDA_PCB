import pytest

from photonx_eda_pcb.aperture_macros import evaluate_macro, parse_macro_body
from photonx_eda_pcb.aperture_macros.lexer import split_macro_statements


def test_code_zero_comment_requires_space_and_is_ignored():
    statements = parse_macro_body("0 human-readable comment*1,1,2.0,0,0*")

    assert len(statements) == 1
    assert statements[0].code == 1


@pytest.mark.parametrize(
    "statement",
    [
        "0",
        "0,not-a-comment",
        "01,1,2.0,0,0",
        "00020,1,0.2,-1,0,1,0",
    ],
)
def test_malformed_or_noncanonical_macro_statement_is_not_silently_ignored(
    statement: str,
):
    with pytest.raises(ValueError, match="unsupported macro statement"):
        parse_macro_body(statement + "*")


def test_macro_newlines_are_whitespace_not_token_concatenation():
    statements = split_macro_statements("1,1,$1\n2,0,0*")

    assert statements == ["1,1,$1 2,0,0"]


def test_multiline_macro_after_delimiter_remains_valid():
    statements = parse_macro_body("1,1,\n2.0,0,\n0*")
    evaluated = evaluate_macro(statements)

    assert evaluated[0]["kind"] == "circle"
    assert evaluated[0]["values"] == pytest.approx([1.0, 2.0, 0.0, 0.0])
