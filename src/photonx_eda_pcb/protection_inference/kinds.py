TOKENS={"tvs":("tvs","transient suppress"),"esd":("esd","esd diode"),"fuse":("fuse","polyfuse","ptc"),"reverse_polarity":("ideal diode","reverse polarity"),"ferrite":("ferrite","bead"),"common_mode_choke":("common mode","cm choke","cmc")}
def protection_kind(identity):
    text=" ".join(str(x or "") for x in (getattr(identity,"kind",None),getattr(identity,"value",None),getattr(identity,"mpn",None))).lower()
    for kind,toks in TOKENS.items():
        if any(t in text for t in toks):return kind
    return None
