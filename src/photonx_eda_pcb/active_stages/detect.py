from photonx_eda_pcb.analog_blocks.model import AnalogBlockCandidate
from photonx_eda_pcb.analog_blocks.ids import block_id
from photonx_eda_pcb.analog_blocks.kinds import is_kind
from photonx_eda_pcb.analog_blocks.topology import nets_for
from .pins import active_pin_roles
def detect_opamp_comparator_stages(identity_by_id,component_pin_nets,pin_names_by_component=None):
    pin_names_by_component=pin_names_by_component or {};out=[]
    for cid,identity in sorted(identity_by_id.items()):
        if not is_kind(identity,"opamp","op_amp","comparator"):continue
        roles=active_pin_roles(pin_names_by_component.get(cid,{}))
        if "output" not in roles or not ({"noninverting","inverting"}&set(roles)):continue
        nets=component_pin_nets.get(cid,{})
        params=[];ev=["active_component_identity","signal_pin_names"];score=.8
        for role,pin in sorted(roles.items()):
            if pin in nets and nets[pin] is not None:params.append((role+"_net",str(nets[pin])))
        if {"noninverting","inverting","output"}<=set(roles):score=.9
        allnets=nets_for(cid,component_pin_nets)
        kind="comparator_stage" if is_kind(identity,"comparator") else "opamp_stage"
        out.append(AnalogBlockCandidate(block_id(kind,(cid,),allnets),kind,(cid,),allnets,score,tuple(ev),tuple(params),("gain_and_function_unresolved",)))
    return out
