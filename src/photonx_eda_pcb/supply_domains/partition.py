from .model import SupplyDomain
from .names import voltage_hint
def partition_supply_domains(power_nets,ground_nets,component_pin_nets):
    grounds=tuple(sorted(map(str,ground_nets)));out=[]
    for p in sorted(map(str,power_nets)):
        comps=[]
        for cid,pins in component_pin_nets.items():
            vals=set(str(x) for x in pins.values() if x is not None)
            if p in vals:comps.append(str(cid))
        out.append(SupplyDomain(p,(p,),grounds,tuple(sorted(comps)),voltage_hint(p),.8 if comps else .55))
    return out
