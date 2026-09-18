def spacing_score(variation_mm,max_variation_mm=.15):return round(max(0.0,1-abs(float(variation_mm))/max(float(max_variation_mm),1e-9)),6)
