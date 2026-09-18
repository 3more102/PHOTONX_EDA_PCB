def constraint_confidence(source_direct=False,stackup_known=False,geometry_known=False):
    return round(min((.5 if source_direct else 0)+(.25 if stackup_known else 0)+(.25 if geometry_known else 0),1.0),12)
