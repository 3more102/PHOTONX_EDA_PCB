from photonx_eda_pcb.architecture_audit import audit_architecture,validate_audit
def test_detects_package_file_collision():
    paths=["src/x/reporting.py","src/x/reporting/__init__.py","src/x/a/model.py","src/x/b/model.py"]
    a=audit_architecture(paths,{"a":["validate"],"b":["validate"],"c":["validate"]})
    codes={x.code for x in a.findings}
    assert "PACKAGE_FILE_COLLISION" in codes and "CAPABILITY_OVERLAP" in codes
    assert validate_audit(a)==[]
