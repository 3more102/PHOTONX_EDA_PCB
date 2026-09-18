from .model import PortCandidate
def infer_ports(resolved_pin_functions):
    by={}
    for p in resolved_pin_functions:by.setdefault(p.connector_id,[]).append(p)
    out=[]
    for cid,items in sorted(by.items()):
        funcs={p.function for p in items if p.function};pairs=[("i2c",{"i2c_sda","i2c_scl"}),("uart",{"uart_tx","uart_rx"}),("can",{"can_h","can_l"}),("usb",{"usb_dp","usb_dm"})]
        matched=False
        for kind,needed in pairs:
            if needed<=funcs:
                sel=[p for p in items if p.function in needed];conf=min(p.confidence for p in sel)
                out.append(PortCandidate(cid,kind,tuple(p.pin for p in sel),tuple(p.net_id for p in sel),conf,("pin_functions",)));matched=True
        spi_needed={"spi_mosi","spi_miso","spi_clock"}
        if spi_needed<=funcs:
            sel=[p for p in items if p.function in spi_needed|{"spi_cs"}];out.append(PortCandidate(cid,"spi",tuple(p.pin for p in sel),tuple(p.net_id for p in sel),min(p.confidence for p in sel),("pin_functions",)));matched=True
        power_sel=[p for p in items if p.function in {"power","ground"}]
        if power_sel:
            out.append(PortCandidate(cid,"power",tuple(p.pin for p in power_sel),tuple(p.net_id for p in power_sel),min(p.confidence for p in power_sel),("power_ground_pins",)))
        if not matched and not power_sel and items:
            out.append(PortCandidate(cid,"generic",tuple(p.pin for p in items),tuple(p.net_id for p in items),round(sum(p.confidence for p in items)/len(items),6),("unclassified_pin_functions",)))
    return out
