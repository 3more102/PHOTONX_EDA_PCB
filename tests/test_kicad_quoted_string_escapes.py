import pytest

from photonx_eda_pcb.kicad_reader.sexpr import parse_sexpr


def test_kicad_simple_escapes_decode_to_original_characters():
    parsed = parse_sexpr(
        r'(value "line\nnext\rreturn\tcolumn\\path\"quoted\"\a\b\f\v")'
    )

    assert parsed == [
        "value",
        'line\nnext\rreturn\tcolumn\\path"quoted"\a\b\f\v',
    ]


def test_kicad_hex_and_octal_escapes_decode_as_utf8_bytes():
    parsed = parse_sexpr(r'(value "\xC3\xA9" "\303\251")')

    assert parsed == ["value", "é", "é"]


def test_unknown_escape_preserves_backslash_and_character():
    assert parse_sexpr(r'(value "net\qname")') == ["value", r"net\qname"]


def test_malformed_hex_escape_matches_kicad_literal_x_behavior():
    assert parse_sexpr(r'(value "\xZ")') == ["value", "xZ"]


def test_escape_bytes_must_form_valid_utf8():
    with pytest.raises(ValueError, match="valid UTF-8"):
        parse_sexpr(r'(value "\xE9")')
