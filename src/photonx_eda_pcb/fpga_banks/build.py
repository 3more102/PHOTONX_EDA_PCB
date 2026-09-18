from .model import FpgaPin,FpgaBank
def build_fpga_banks(component_id,pin_metadata):
    groups={}
    for pin,data in pin_metadata.items():
        bank=str(data.get("bank","unknown"))
        groups.setdefault(bank,[]).append(FpgaPin(str(pin),None if data.get("net_id") is None else str(data.get("net_id")),bank,data.get("io_standard"),data.get("voltage")))
    out=[]
    for bank,pins in sorted(groups.items()):
        volts=[float(x.voltage) for x in pins if x.voltage is not None]
        supply=round(sum(volts)/len(volts),6) if volts else None
        conf=.85 if bank!="unknown" else .45
        out.append(FpgaBank(str(component_id),bank,tuple(sorted(pins,key=lambda x:x.pin)),supply,conf))
    return out
