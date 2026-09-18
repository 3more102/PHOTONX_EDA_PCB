from photonx_eda_pcb.analog_blocks.model import AnalogBlockCandidate
from photonx_eda_pcb.analog_blocks.ids import block_id
from photonx_eda_pcb.analog_blocks.kinds import is_kind
from photonx_eda_pcb.analog_blocks.topology import components_on_net,nets_for
from .pins import feedback_pins
def detect_feedback_networks(identity_by_id,component_pin_nets,pin_names_by_component=None):
    pin_names_by_component=pin_names_by_component or {};out=[]
    for cid,identity in sorted(identity_by_id.items()):
        if not is_kind(identity,"opamp","op_amp","comparator","regulator","converter"):continue
        fb=feedback_pins(pin_names_by_component.get(cid,{}))
        for pin in fb:
            net=component_pin_nets.get(cid,{}).get(pin)
            if net is None:continue
            attached=[c for c in components_on_net(net,component_pin_nets) if c!=cid]
            passive=[c for c in attached if c in identity_by_id and is_kind(identity_by_id[c],"resistor","capacitor")]
            if not passive:continue
            comps=(cid,*tuple(sorted(passive)));nets=tuple(sorted({n for c in comps for n in nets_for(c,component_pin_nets)}))
            score=.88 if len(passive)>=2 else .75
            out.append(AnalogBlockCandidate(block_id("feedback_network",comps,nets),"feedback_network",comps,nets,score,("feedback_pin_name","passive_network"),(("feedback_pin",pin),("feedback_net",str(net))),("closed_loop_function_unverified",)))
    return out
