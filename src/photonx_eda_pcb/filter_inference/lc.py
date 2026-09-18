from photonx_eda_pcb.analog_blocks.model import AnalogBlockCandidate
from photonx_eda_pcb.analog_blocks.ids import block_id
from photonx_eda_pcb.analog_blocks.kinds import is_kind
from photonx_eda_pcb.analog_blocks.topology import nets_for,shared_nets
from photonx_eda_pcb.analog_blocks.values import parse_inductance,parse_capacitance
from .cutoff import lc_resonance_hz
def detect_lc_filters(identity_by_id,component_pin_nets,ground_nets=()):
    ls=sorted(c for c,i in identity_by_id.items() if is_kind(i,"inductor","ferrite"));cs=sorted(c for c,i in identity_by_id.items() if is_kind(i,"capacitor"));g=set(map(str,ground_nets));out=[]
    for l in ls:
        for c in cs:
            shared=shared_nets(l,c,component_pin_nets)
            if len(shared)!=1:continue
            ln=set(nets_for(l,component_pin_nets));cn=set(nets_for(c,component_pin_nets));cother=cn-set(shared)
            if len(ln)!=2 or len(cn)!=2:continue
            grounded=bool(cother&g);score=.8 if grounded else .6;ev=["inductor_capacitor_shared_node"]+(["capacitor_to_ground"] if grounded else [])
            lv=parse_inductance(getattr(identity_by_id[l],"value",None));cv=parse_capacitance(getattr(identity_by_id[c],"value",None));params=[("junction",shared[0])]
            ass=["filter_function_unproven"]
            if lv and cv:params.append(("estimated_resonance_hz",round(lc_resonance_hz(lv,cv),6)));ev.append("component_values")
            else:ass.append("component_values_incomplete")
            nets=tuple(sorted(ln|cn));out.append(AnalogBlockCandidate(block_id("lc_filter",(l,c),nets),"lc_filter",(l,c),nets,score,tuple(ev),tuple(params),tuple(ass)))
    return out
