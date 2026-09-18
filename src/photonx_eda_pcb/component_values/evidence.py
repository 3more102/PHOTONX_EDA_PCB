def combine_value_evidence(marking=False,bom=False,reference_designator=False):
    return round(min((.5 if marking else 0)+(.4 if bom else 0)+(.1 if reference_designator else 0),1),12)
