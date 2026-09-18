from photonx_eda_pcb.analog_blocks.model import AnalogBlockCandidate
from photonx_eda_pcb.analog_blocks.ids import block_id
from photonx_eda_pcb.analog_blocks.kinds import is_kind
from photonx_eda_pcb.analog_blocks.topology import nets_for,shared_nets
from photonx_eda_pcb.analog_blocks.values import parse_resistance,parse_capacitance
from .cutoff import rc_cutoff_hz
def detect_rc_filters(identity_by_id,component_pin_nets,ground_nets=()):
    rs=sorted(c for c,i in identity_by_id.items() if is_kind(i,"resistor"));cs=sorted(c for c,i in identity_by_id.items() if is_kind(i,"capacitor"));g=set(map(str,ground_nets));out=[]
    for r in rs:
        for c in cs:
            shared=shared_nets(r,c,component_pin_nets)
            if len(shared)!=1:continue
            rn=set(nets_for(r,component_pin_nets));cn=set(nets_for(c,component_pin_nets))
            cother=cn-set(shared)
            if len(rn)!=2 or len(cn)!=2 or len(cother)!=1:continue
            grounded=bool(cother&g);score=.82 if grounded else .62;ev=["resistor_capacitor_shared_node"]+(["capacitor_to_ground"] if grounded else [])
            rv=parse_resistance(getattr(identity_by_id[r],"value",None));cv=parse_capacitance(getattr(identity_by_id[c],"value",None));params=[("junction",shared[0])]
            assumptions=["filter_function_unproven"]
            if rv and cv:
                params.append(("estimated_cutoff_hz",round(rc_cutoff_hz(rv,cv),6)));ev.append("component_values")
            else:assumptions.append("component_values_incomplete")
            nets=tuple(sorted(rn|cn));out.append(AnalogBlockCandidate(block_id("rc_filter",(r,c),nets),"rc_filter",(r,c),nets,score,tuple(ev),tuple(params),tuple(assumptions)))
    return out
