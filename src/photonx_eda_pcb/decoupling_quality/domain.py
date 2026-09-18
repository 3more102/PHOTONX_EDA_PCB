def domain_quality(items,power_net):
    vals=[x.score*x.confidence for x in items if x.power_net==power_net]
    return 0.0 if not vals else round(sum(vals)/len(vals),6)
