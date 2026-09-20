from photonx_eda_pcb.kicad_identity import photonx_uuid


def test_photonx_uuid_contract_is_stable():
    assert photonx_uuid("track:T1") == "c368f1f3-3b3a-5ba4-96c5-191e35626ac5"
    assert photonx_uuid("fp:P1") == "e6e1db9f-1335-5d89-8b56-36dd202f9dc9"
    assert photonx_uuid("region:R1") == "355e3739-0f4f-531c-a6d1-0626d1a79721"
    assert photonx_uuid("slot-fp:S1") == "3689c068-5a6a-5bc2-a54f-bdb134aca7b9"
