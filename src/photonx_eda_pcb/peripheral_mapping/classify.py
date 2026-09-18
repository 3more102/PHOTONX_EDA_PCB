CONTROLLER_HINTS=("mcu","microcontroller","cpu","soc","fpga","processor","controller")
def is_controller(identity):
    text=" ".join(str(getattr(identity,x,"") or "").lower() for x in ("kind","value","mpn"))
    return any(h in text for h in CONTROLLER_HINTS)
def endpoint_role(component_id,components):
    ident=components.get(str(component_id))
    return "controller" if ident is not None and is_controller(ident) else "peripheral"
