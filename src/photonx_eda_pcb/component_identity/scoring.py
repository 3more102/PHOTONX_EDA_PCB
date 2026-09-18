SOURCE_WEIGHT={"bom":1.0,"pick_place":.9,"marking":.75,"footprint_match":.65,"geometry":.5,"heuristic":.35}
def weighted_confidence(candidate):return round(min(1.0,float(candidate.confidence)*SOURCE_WEIGHT.get(candidate.source,.5)),12)
