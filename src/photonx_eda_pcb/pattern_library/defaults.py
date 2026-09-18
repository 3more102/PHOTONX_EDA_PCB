from .model import PatternDefinition
def default_patterns():
    return [PatternDefinition("two_part_passive",("resistor","capacitor"),2,4,(),"Generic passive pair"),PatternDefinition("led_resistor_channel",("led","resistor"),2,5,(),"LED plus resistor channel"),PatternDefinition("sensor_interface",("sensor",),1,None,("i2c",),"Sensor interface candidate"),PatternDefinition("power_stage",("regulator",),1,None,("power",),"Power-stage candidate"),PatternDefinition("connector_interface",("connector",),1,None,(),"External interface candidate")]
