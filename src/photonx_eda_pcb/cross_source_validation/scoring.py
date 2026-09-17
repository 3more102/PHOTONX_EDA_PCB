SOURCE_WEIGHT={'ipc356':1.0,'source_cad':1.0,'kicad':0.95,'bom':0.9,'pick_place':0.85,'gerber_x2':0.8,'silkscreen':0.55,'geometry_inference':0.4}

def source_weight(name):return SOURCE_WEIGHT.get(str(name).lower(),0.25)

def weighted_confidence(observation):return round(min(float(observation.confidence)*source_weight(observation.source),1.0),12)
