def return_support_score(nearby_return_vias):
    n=max(0,int(nearby_return_vias))
    return round(min(1.0,n/2.0),6)
