from .stats import schematic_stats
def roundtrip_report(data,differences=()):return {"stats":schematic_stats(data),"differences":list(differences),"roundtrip_equal":not differences}
