def symbol_confidence(kind_match=False,pin_count_match=False,reference_prefix=False,bom_match=False):
    return round(min((.35 if kind_match else 0)+(.25 if pin_count_match else 0)+(.1 if reference_prefix else 0)+(.3 if bom_match else 0),1),12)
