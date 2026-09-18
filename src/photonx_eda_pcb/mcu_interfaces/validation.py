def validate_mcu_interface(x):
    issues=[]
    if not x.component_id:issues.append("MCU_INTERFACE_COMPONENT_EMPTY")
    if not x.protocol:issues.append("MCU_INTERFACE_PROTOCOL_EMPTY")
    if not 0<=x.confidence<=1:issues.append("MCU_INTERFACE_CONFIDENCE_RANGE")
    return issues
