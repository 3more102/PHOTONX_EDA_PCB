def classify_channel(component_kinds,net_roles=()):
    kinds={str(x).lower() for x in component_kinds};roles={str(x).lower() for x in net_roles}
    if any("led" in x for x in kinds) and any("resistor" in x or x=="r" for x in kinds):return "led_driver"
    if any("sensor" in x for x in kinds):return "sensor_channel"
    if any("opamp" in x or "op_amp" in x for x in kinds):return "analog_front_end"
    if any("regulator" in x or "converter" in x for x in kinds) or "power" in roles:return "power_stage"
    if any("connector" in x for x in kinds):return "connector_channel"
    return "repeated_channel"
