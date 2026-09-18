from photonx_eda_pcb.analog_blocks.model import AnalogBlockCandidate
from photonx_eda_pcb.analog_blocks.ids import block_id
from photonx_eda_pcb.analog_blocks.kinds import is_kind
from photonx_eda_pcb.analog_blocks.topology import nets_for
def detect_pull_networks(identity_by_id,component_pin_nets,power_nets=(),ground_nets=()):
    p=set(map(str,power_nets));g=set(map(str,ground_nets));out=[]
    for cid,i in sorted(identity_by_id.items()):
        if not is_kind(i,"resistor"):continue
        nets=nets_for(cid,component_pin_nets)
        if len(nets)!=2:continue
        s=set(nets);anchors=(s&p,s&g)
        if bool(anchors[0])==bool(anchors[1]):continue
        anchor=next(iter(anchors[0] or anchors[1]));signal=next(iter(s-{anchor}))
        kind="pull_up" if anchor in p else "pull_down"
        out.append(AnalogBlockCandidate(block_id(kind,(cid,),nets),kind,(cid,),nets,.72,("resistor_to_supply",),(("signal_net",signal),("anchor_net",anchor)),("signal_role_unverified",)))
    return out
