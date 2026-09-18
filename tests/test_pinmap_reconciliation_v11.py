from photonx_eda_pcb.pinmap_reconciliation import reconcile_pinmap,validate_pinmap_report
from photonx_eda_pcb.pinmap_reconciliation.coverage import pinmap_coverage
def test_pinmap_reconciliation():
    r=reconcile_pinmap("U1",{"1":"VCC","2":"GND","3":"OUT"},{"1":"VCC","2":"GND","3":"SIG"})
    assert r.matched==2 and any(x.code=="PIN_NAME_MISMATCH" for x in r.issues)
    assert pinmap_coverage(r)==round(2/3,6)
    assert validate_pinmap_report(r)==[]
