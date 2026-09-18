def common_mode_chokes(components):
    out=[]
    for c in components:
        text=(str(getattr(c,"kind",""))+" "+str(getattr(c,"value",""))).lower()
        if "common mode" in text or "cmc" in text or "common-mode" in text:out.append(str(c.id))
    return sorted(out)
