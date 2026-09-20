import math

import pytest

from photonx_eda_pcb.exporters.json_export import export_json
from photonx_eda_pcb.io.json_codec import dump_json, load_json
from photonx_eda_pcb.serialization.canonical import dumps_canonical
from photonx_eda_pcb.serialization.json_policy import dumps_strict, loads_strict
from photonx_eda_pcb.serialization.ndjson import decode_records, encode_records


class _NonFiniteBoard:
    def to_dict(self):
        return {"metric": math.nan}


def test_strict_json_rejects_non_finite_numbers_in_both_directions():
    with pytest.raises(ValueError, match="Out of range float values"):
        dumps_strict({"value": math.nan})

    for literal in ("NaN", "Infinity", "-Infinity"):
        with pytest.raises(ValueError, match="non-finite JSON numeric literal"):
            loads_strict('{"value": ' + literal + "}")


def test_strict_json_rejects_duplicate_object_keys_at_any_depth():
    with pytest.raises(ValueError, match="duplicate JSON object key"):
        loads_strict('{"outer": {"id": 1, "id": 2}}')


def test_canonical_and_ndjson_share_the_strict_policy():
    assert dumps_canonical({"b": 1, "a": 2}) == '{"a":2,"b":1}'

    with pytest.raises(ValueError):
        dumps_canonical({"value": math.inf})

    with pytest.raises(ValueError):
        encode_records([{"value": math.nan}])

    with pytest.raises(ValueError, match="duplicate JSON object key"):
        decode_records('{"id":1,"id":2}\n')


def test_core_json_file_codec_is_strict(tmp_path):
    valid = tmp_path / "valid.json"
    dump_json({"b": 1, "a": 2}, valid)
    assert load_json(valid) == {"a": 2, "b": 1}

    with pytest.raises(ValueError):
        dump_json({"value": -math.inf}, tmp_path / "invalid-output.json")

    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"id":1,"id":2}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON object key"):
        load_json(duplicate)

    non_finite = tmp_path / "non-finite.json"
    non_finite.write_text('{"value":NaN}', encoding="utf-8")
    with pytest.raises(ValueError, match="non-finite JSON numeric literal"):
        load_json(non_finite)


def test_board_json_export_does_not_emit_non_standard_nan(tmp_path):
    target = tmp_path / "board.json"
    with pytest.raises(ValueError):
        export_json(_NonFiniteBoard(), target)
    assert not target.exists()
