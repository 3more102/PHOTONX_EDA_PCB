def skew_score(skew_mm,max_skew_mm=.5):return round(max(0.0,1-abs(float(skew_mm))/max(float(max_skew_mm),1e-9)),6)
