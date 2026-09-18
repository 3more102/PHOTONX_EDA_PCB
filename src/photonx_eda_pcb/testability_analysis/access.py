def accessible_testpoints(testpoints,min_diameter_mm=.6,min_confidence=.5):
    return [tp for tp in testpoints if tp.exposed and float(tp.diameter_mm)>=float(min_diameter_mm) and float(tp.confidence)>=float(min_confidence)]
