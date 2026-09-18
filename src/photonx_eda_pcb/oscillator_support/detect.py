from photonx_eda_pcb.analog_blocks.model import AnalogBlockCandidate
from photonx_eda_pcb.analog_blocks.ids import block_id
from photonx_eda_pcb.analog_blocks.kinds import is_kind
from photonx_eda_pcb.analog_blocks.topology import nets_for,components_on_net
def detect_oscillator_support(identity_by_id,component_pin_nets,ground_nets=()):
    g=set(map(str,ground_nets));out=[]
    for cid,identity in sorted(identity_by_id.items()):
        if not is_kind(identity,"crystal","oscillator","resonator"):continue
        xnets=nets_for(cid,component_pin_nets)
        support=set()
        for n in xnets:
            for c in components_on_net(n,component_pin_nets):
                if c==cid or c not in identity_by_id:continue
                if is_kind(identity_by_id[c],"capacitor","resistor"):support.add(c)
        grounded_caps=[]
        for c in support:
            if is_kind(identity_by_id[c],"capacitor") and set(nets_for(c,component_pin_nets))&g:grounded_caps.append(c)
        comps=(cid,*tuple(sorted(support)));allnets=tuple(sorted({n for c in comps for n in nets_for(c,component_pin_nets)}))
        score=.7+.08*min(len(support),2)+(.08 if grounded_caps else 0)
        ev=["frequency_component_identity"]+(["support_passives"] if support else [])+(["grounded_load_capacitor"] if grounded_caps else [])
        out.append(AnalogBlockCandidate(block_id("oscillator_support",comps,allnets),"oscillator_support",comps,allnets,round(min(score,1),6),tuple(ev),(("grounded_capacitors",len(grounded_caps)),),("oscillation_mode_unresolved",)))
    return out
