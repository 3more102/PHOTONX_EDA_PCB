def board_thermal_score(items):
    vals=[x.risk*x.confidence for x in items]
    return 0.0 if not vals else round(sum(vals)/len(vals),6)
