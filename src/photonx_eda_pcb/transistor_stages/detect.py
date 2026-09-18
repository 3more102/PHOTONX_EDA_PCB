from photonx_eda_pcb.analog_blocks.model import AnalogBlockCandidate
from photonx_eda_pcb.analog_blocks.ids import block_id
from photonx_eda_pcb.analog_blocks.kinds import is_kind
from photonx_eda_pcb.analog_blocks.topology import components_on_net,nets_for
from .pins import transistor_pin_roles
def detect_transistor_stages(identity_by_id,component_pin_nets,pin_names_by_component=None,power_nets=(),ground_nets=()):
    pin_names_by_component=pin_names_by_component or {};p=set(map(str,power_nets));g=set(map(str,ground_nets));out=[]
    for cid,identity in sorted(identity_by_id.items()):
        if not is_kind(identity,"transistor","mosfet","bjt","fet"):continue
        roles=transistor_pin_roles(pin_names_by_component.get(cid,{}))
        if "control" not in roles:continue
        nets=component_pin_nets.get(cid,{})
        cnet=nets.get(roles["control"]);snet=nets.get(roles.get("source",""));lnet=nets.get(roles.get("load",""))
        attached=components_on_net(cnet,component_pin_nets) if cnet is not None else []
        bias=[c for c in attached if c!=cid and c in identity_by_id and is_kind(identity_by_id[c],"resistor")]
        ev=["transistor_identity","control_pin"];score=.65
        if bias:ev.append("control_bias_resistor");score+=.12
        if snet is not None and str(snet) in g:ev.append("source_to_ground");score+=.1
        if snet is not None and str(snet) in p:ev.append("source_to_power");score+=.08
        comps=(cid,*tuple(sorted(bias)));allnets=tuple(sorted({n for c in comps for n in nets_for(c,component_pin_nets)}))
        out.append(AnalogBlockCandidate(block_id("transistor_stage",comps,allnets),"transistor_stage",comps,allnets,round(min(score,1),6),tuple(ev),(("control_net",None if cnet is None else str(cnet)),("load_net",None if lnet is None else str(lnet))),("switch_or_amplifier_role_unresolved",)))
    return out
