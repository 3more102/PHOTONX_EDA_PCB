from photonx_eda_pcb.controlled_impedance.parser import parse_constraint
def test_constraint_parser():
    c=parse_constraint("CLK:50:5:single-ended")
    assert c.net_id=="CLK" and c.target_ohms==50 and c.tolerance_ohms==5
