import pytest

from photonx_eda_pcb.parsers.common.attributes import parse_attribute_fields
from photonx_eda_pcb.parsers.gerber_parts.attributes import parse_x2_attribute


def test_fields():
    assert parse_attribute_fields("%TF.FileFunction,Copper,L1,Top*%") == (
        ".FileFunction",
        ["Copper", "L1", "Top"],
    )


def test_x2():
    assert parse_x2_attribute("%TA.AperFunction,Conductor*%") == {
        "name": ".AperFunction",
        "values": ["Conductor"],
    }


def test_user_attribute_name_is_preserved():
    assert parse_attribute_fields("%TFMyAttribute,Yes*%") == (
        "MyAttribute",
        ["Yes"],
    )


def test_unicode_escapes_decode_after_field_splitting():
    assert parse_attribute_fields(r"%TF.MyText,alpha\u002Cbeta*%") == (
        ".MyText",
        ["alpha,beta"],
    )


def test_reserved_and_non_ascii_characters_can_be_escaped():
    assert parse_attribute_fields(
        r"%TF.MyText,\u0025\u002A\u005C\U0001F4A1*%"
    ) == (".MyText", ["%*\\💡"])


def test_field_whitespace_is_data_not_parser_padding():
    assert parse_attribute_fields("%TF.MyText,  spaced text  *%") == (
        ".MyText",
        ["  spaced text  "],
    )


def test_delete_all_attributes_has_no_name_or_values():
    assert parse_attribute_fields("%TD*%") == ("", [])


@pytest.mark.parametrize(
    "attribute",
    [
        r"%TF.MyText,abc\def*%",
        r"%TF.MyText,\u12*%",
        r"%TF.MyText,\uD800*%",
        r"%TF.MyText,\U00110000*%",
        "%TF.MyText,raw%percent*%",
        "%TF.9Bad,value*%",
    ],
)
def test_malformed_attribute_text_fails_closed(attribute):
    with pytest.raises(ValueError):
        parse_attribute_fields(attribute)
