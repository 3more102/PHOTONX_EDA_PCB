import pytest
from photonx_eda_pcb.serialization.canonical import dumps_canonical
from photonx_eda_pcb.serialization.ndjson import encode_records,decode_records
from photonx_eda_pcb.serialization.versioning import require_supported
def test_serialization_contracts():
    assert dumps_canonical({"b":1,"a":2})=='{"a":2,"b":1}'
    records=[{"a":1},{"b":2}]; assert decode_records(encode_records(records))==records
    assert require_supported("1.2")== (1,2)
    with pytest.raises(ValueError): require_supported("9.0")
