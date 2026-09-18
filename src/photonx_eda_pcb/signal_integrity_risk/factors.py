def normalized_factor(value,good,bad):
    v=float(value);g=float(good);b=float(bad)
    if b==g:return 0.0
    return round(min(1.0,max(0.0,(v-g)/(b-g))),6)
def via_factor(via_count):return round(min(1.0,max(0,int(via_count))/8.0),6)
def skew_factor(skew_mm,target_mm=.5):return round(min(1.0,abs(float(skew_mm))/max(float(target_mm),1e-9)),6)
