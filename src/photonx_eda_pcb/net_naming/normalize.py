def normalize_net_name(name):
    s=" ".join(str(name or "").strip().split())
    return s.replace(" ","_") if s else ""
