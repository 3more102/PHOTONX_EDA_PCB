KIND_PREFIX={"resistor":"R","capacitor":"C","inductor":"L","led":"D","diode":"D","connector":"J","ic":"U","integrated_circuit":"U","transistor":"Q","testpoint":"TP","fuse":"F"}
def prefix_for_kind(kind):return KIND_PREFIX.get(str(kind).lower(),"U")
