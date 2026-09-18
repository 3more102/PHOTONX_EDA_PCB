from photonx_eda_pcb.controlled_impedance import ImpedanceConstraint,check_constraint,validate_constraint
def test_impedance_constraint():
    c=ImpedanceConstraint("USB",90,8,"differential")
    x=check_constraint(c,94,.8)
    assert x.passed is True and x.error_ohms==4
    assert validate_constraint(c)==[]
