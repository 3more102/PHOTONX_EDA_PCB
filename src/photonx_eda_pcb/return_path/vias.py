def return_via_penalty(signal_vias,nearby_return_vias,max_spacing_mm=2.0):
    if signal_vias<=0:return 0.0
    covered=min(int(signal_vias),int(nearby_return_vias))
    return round(1.0-covered/max(int(signal_vias),1),6)
