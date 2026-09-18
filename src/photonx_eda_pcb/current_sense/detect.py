from photonx_eda_pcb.analog_blocks.model import AnalogBlockCandidate
from photonx_eda_pcb.analog_blocks.ids import block_id
from photonx_eda_pcb.analog_blocks.kinds import is_kind
from photonx_eda_pcb.analog_blocks.topology import nets_for
from photonx_eda_pcb.analog_blocks.values import parse_resistance
def detect_current_sense(identity_by_id,component_pin_nets,max_shunt_ohm=1.0):
    out=[]
    for cid,identity in sorted(identity_by_id.items()):
        if not is_kind(identity,"resistor","shunt","current_sense"):continue
        value=parse_resistance(getattr(identity,"value",None))
        direct=is_kind(identity,"shunt","current_sense")
        if not direct and (value is None or value>float(max_shunt_ohm)):continue
        nets=nets_for(cid,component_pin_nets)
        if len(nets)!=2:continue
        score=.9 if direct else .58;ev=["shunt_identity"] if direct else ["low_resistance_value"]
        params=(("resistance_ohm",value),) if value is not None else ()
        out.append(AnalogBlockCandidate(block_id("current_sense",(cid,),nets),"current_sense",(cid,),nets,score,tuple(ev),params,("current_measurement_function_unproven",)))
    return out
