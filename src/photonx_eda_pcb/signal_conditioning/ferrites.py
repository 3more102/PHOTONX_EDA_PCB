def ferrite_components(components):
    out=[]
    for c in components:
        text=(str(getattr(c,"kind",""))+" "+str(getattr(c,"value",""))).lower()
        if "ferrite" in text or "bead" in text:out.append(str(c.id))
    return sorted(out)
