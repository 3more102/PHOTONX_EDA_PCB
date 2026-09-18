DDR_KINDS={"ddr","ddr2","ddr3","ddr4","ddr5","lpddr","lpddr4","lpddr5","memory_controller","dram"}
def classify_components(identity_by_id):
    controllers=[];memories=[]
    for cid,identity in identity_by_id.items():
        k=str(getattr(identity,"kind","") or "").lower()
        value=str(getattr(identity,"value","") or "").lower()
        text=k+" "+value
        if "controller" in text or any(x in text for x in ("soc","fpga","cpu")):controllers.append(str(cid))
        if any(x in text for x in DDR_KINDS if x!="memory_controller"):memories.append(str(cid))
    return sorted(controllers),sorted(memories)
