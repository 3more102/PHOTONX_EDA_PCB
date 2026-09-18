def normalize_rotation(deg):
    v=float(deg)%360.0
    return 0.0 if abs(v-360.0)<1e-12 else round(v,12)
