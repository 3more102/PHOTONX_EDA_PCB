def edge_biases(component_kinds):
    out={}
    for cid,kind in component_kinds.items():
        k=str(kind).lower()
        if "connector" in k:out[str(cid)]="left"
        elif any(x in k for x in ("regulator","power","supply")):out[str(cid)]="top"
        elif any(x in k for x in ("mcu","cpu","fpga","soc")):out[str(cid)]="center"
    return out
