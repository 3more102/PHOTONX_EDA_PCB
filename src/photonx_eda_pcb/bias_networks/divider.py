from photonx_eda_pcb.analog_blocks.model import AnalogBlockCandidate
from photonx_eda_pcb.analog_blocks.ids import block_id
from photonx_eda_pcb.analog_blocks.kinds import is_kind
from photonx_eda_pcb.analog_blocks.topology import nets_for,shared_nets
def detect_voltage_dividers(identity_by_id,component_pin_nets,power_nets=(),ground_nets=()):
    resistors=sorted(cid for cid,i in identity_by_id.items() if is_kind(i,"resistor"))
    p=set(map(str,power_nets));g=set(map(str,ground_nets));out=[]
    for ix,a in enumerate(resistors):
        for b in resistors[ix+1:]:
            shared=shared_nets(a,b,component_pin_nets)
            if len(shared)!=1:continue
            na=set(nets_for(a,component_pin_nets));nb=set(nets_for(b,component_pin_nets))
            oa=na-set(shared);ob=nb-set(shared)
            if len(oa)!=1 or len(ob)!=1:continue
            outer={next(iter(oa)),next(iter(ob))}
            ev=["two_resistors_series","single_midpoint"];score=.62
            if outer&p and outer&g:score=.9;ev+=["power_anchor","ground_anchor"]
            elif outer&(p|g):score=.75;ev.append("one_supply_anchor")
            nets=tuple(sorted(na|nb))
            out.append(AnalogBlockCandidate(block_id("voltage_divider",(a,b),nets),"voltage_divider",(a,b),nets,score,tuple(ev),(("midpoint",shared[0]),),("function_unproven",)))
    return out
