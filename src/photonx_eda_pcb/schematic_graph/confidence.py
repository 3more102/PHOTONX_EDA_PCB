def graph_confidence(net_confidences,component_confidences):
    vals=[float(v) for v in [*net_confidences,*component_confidences]]
    return round(sum(vals)/len(vals),12) if vals else 0.0
