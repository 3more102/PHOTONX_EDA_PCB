from photonx_eda_pcb.pinmap_reconciliation.netmap import reconcile_pin_nets
def test_pin_net_mismatch():
    out=reconcile_pin_nets({"1":"VCC","2":"GND"},{"1":"VCC","2":"SIG","3":"NC"})
    assert ("2","NET_MISMATCH","GND","SIG") in out
    assert any(x[1]=="UNEXPECTED_NET" for x in out)
