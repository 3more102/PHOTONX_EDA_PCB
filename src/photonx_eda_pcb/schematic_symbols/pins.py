from .model import PinDefinition
def generic_pins(count):
    return [PinDefinition(str(i+1)) for i in range(int(count))]
def named_two_pin(kind):
    k=str(kind).lower()
    if k=="led" or k=="diode":return [PinDefinition("1","K"),PinDefinition("2","A")]
    return generic_pins(2)
