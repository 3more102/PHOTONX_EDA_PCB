from photonx_eda_pcb.bias_networks.divider import detect_voltage_dividers
from photonx_eda_pcb.bias_networks.pulls import detect_pull_networks
from photonx_eda_pcb.filter_inference.rc import detect_rc_filters
from photonx_eda_pcb.filter_inference.lc import detect_lc_filters
from photonx_eda_pcb.feedback_networks.detect import detect_feedback_networks
from photonx_eda_pcb.transistor_stages.detect import detect_transistor_stages
from photonx_eda_pcb.active_stages.detect import detect_opamp_comparator_stages
from photonx_eda_pcb.current_sense.detect import detect_current_sense
from photonx_eda_pcb.oscillator_support.detect import detect_oscillator_support
def detect_analog_blocks(identity_by_id,component_pin_nets,*,power_nets=(),ground_nets=(),pin_names_by_component=None):
    out=[]
    out+=detect_voltage_dividers(identity_by_id,component_pin_nets,power_nets,ground_nets)
    out+=detect_pull_networks(identity_by_id,component_pin_nets,power_nets,ground_nets)
    out+=detect_rc_filters(identity_by_id,component_pin_nets,ground_nets)
    out+=detect_lc_filters(identity_by_id,component_pin_nets,ground_nets)
    out+=detect_feedback_networks(identity_by_id,component_pin_nets,pin_names_by_component)
    out+=detect_transistor_stages(identity_by_id,component_pin_nets,pin_names_by_component,power_nets,ground_nets)
    out+=detect_opamp_comparator_stages(identity_by_id,component_pin_nets,pin_names_by_component)
    out+=detect_current_sense(identity_by_id,component_pin_nets)
    out+=detect_oscillator_support(identity_by_id,component_pin_nets,ground_nets)
    uniq={}
    for x in out:uniq[x.id]=x
    return [uniq[k] for k in sorted(uniq)]
