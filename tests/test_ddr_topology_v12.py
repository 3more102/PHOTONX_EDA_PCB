from photonx_eda_pcb.ddr_topology import infer_ddr_topology,validate_ddr_topology
def test_ddr_topology_from_labels():
    labels={"d0":"DQ0","d1":"DQ1","a0":"A0","a1":"A1","ckp":"CKP","ckn":"CKN","dqs":"DQS0"}
    t=infer_ddr_topology(labels,{})
    roles={x.role for x in t.lanes}
    assert {"data","address","clock","strobe"}<=roles
    assert t.confidence>0 and validate_ddr_topology(t)==[]
