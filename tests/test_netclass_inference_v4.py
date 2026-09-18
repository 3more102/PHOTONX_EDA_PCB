from photonx_eda_pcb.netclass_inference import infer_net_classes,validate_net_classes
def test_netclasses():
    out=infer_net_classes([{"net_id":"1","label":"GND"},{"net_id":"2","label":"USB_D_P","is_diff":True},{"net_id":"3","label":"+3V3"}])
    by={x.net_id:x.class_name for x in out}
    assert by=={"1":"ground","2":"differential","3":"power"}
    assert validate_net_classes(out)==[]
