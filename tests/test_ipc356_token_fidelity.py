import pytest

from photonx_eda_pcb.ipc356 import parse_record
from photonx_eda_pcb.ipc356.tokenize import key_values


def test_key_values_preserves_source_value_case():
    fields = key_values("317 net=Signal_A ref=U1a pin=a1 side=Top")
    assert fields == {
        "NET": "Signal_A",
        "REF": "U1a",
        "PIN": "a1",
        "SIDE": "Top",
    }


def test_parse_record_preserves_evidence_values_with_case_insensitive_keys():
    record = parse_record(
        "317 net=Signal_A ref=U1a pin=a1 x=001000 y=-002000 side=Top"
    )
    assert record is not None
    assert record.net_name == "Signal_A"
    assert record.reference == "U1a"
    assert record.pin == "a1"
    assert record.side == "Top"
    assert record.x == 1.0
    assert record.y == -2.0
    assert record.attributes["NET"] == "Signal_A"


@pytest.mark.parametrize(
    "line",
    [
        "317 NET=GND NET=VSS X=001000 Y=002000",
        "317 net=GND NET=VSS X=001000 Y=002000",
        "317 X=001000 x=002000 Y=003000",
    ],
)
def test_duplicate_fields_are_rejected(line):
    with pytest.raises(ValueError, match=r"duplicate IPC-356 field: (NET|X)"):
        parse_record(line)
