def io_standard_conflicts(bank):
    standards={x.io_standard for x in bank.pins if x.io_standard}
    return sorted(standards) if len(standards)>1 else []
def voltage_conflicts(bank,tolerance=.15):
    vals=[float(x.voltage) for x in bank.pins if x.voltage is not None]
    return bool(vals and max(vals)-min(vals)>float(tolerance))
