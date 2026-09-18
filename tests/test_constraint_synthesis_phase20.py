from photonx_eda_pcb.constraint_synthesis import synthesize_constraints,validate_constraint_set
def test_constraint_synthesis_roles():
    s=synthesize_constraints(["g","p","clk"],{"g":("ground",),"p":("power",),"clk":("clock",)},{"clk":20.0},observed_widths={"p":[.4]})
    by={x.net_id:x for x in s.constraints}
    assert by["p"].min_width_mm>=.3 and by["g"].clearance_mm==.15 and by["clk"].target_length_mm==20
    assert validate_constraint_set(s)==[]
