from photonx_eda_pcb.net_naming.normalize import normalize_net_name
def test_net_name_normalization():
    assert normalize_net_name(" USB D+ ")=="USB_D+"
