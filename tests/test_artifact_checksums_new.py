from photonx_eda_pcb.artifact_catalog.checksums import sha256_text,valid_sha256

def test_checksum_validation():
    h=sha256_text('photonx');assert valid_sha256(h)
    assert not valid_sha256('abc')
