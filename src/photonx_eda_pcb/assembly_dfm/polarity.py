POLAR_KINDS={"diode","led","electrolytic_capacitor","tantalum_capacitor","ic"}
def requires_polarity_mark(kind):return str(kind).lower() in POLAR_KINDS
