from photonx_eda_pcb.diagnostic_catalog import default_catalog,validate_catalog
def test_default_diagnostic_catalog():
    c=default_catalog()
    assert c.get("UNSUPPORTED_SYNTAX").severity=="critical"
    assert c.find("provenance")
    assert validate_catalog(c)==[]
