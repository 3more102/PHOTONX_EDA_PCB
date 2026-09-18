from .model import TopologyFinding,TopologyCoherenceReport
def analyze_topology_coherence(supply_domains=(),pin_functions=(),protocols=()):
    out=[];domain_by_net={}
    for d in supply_domains:
        for n in d.supply_nets:domain_by_net.setdefault(n,[]).append(d.name)
        for n in d.ground_nets:domain_by_net.setdefault(n,[]).append(d.name)
    for p in pin_functions:
        fn=str(p.function or "").lower()
        if fn in {"power","ground"} and p.net_id not in domain_by_net:
            out.append(TopologyFinding("CONNECTOR_POWER_WITHOUT_DOMAIN","warning",f"{p.connector_id}:{p.pin}",p.net_id))
        if fn not in {"power","ground"} and len(domain_by_net.get(p.net_id,()))>1:
            out.append(TopologyFinding("SIGNAL_NET_MULTI_DOMAIN","info",p.net_id,",".join(sorted(domain_by_net[p.net_id]))))
    protocol_nets={n for p in protocols for n in p.net_ids}
    for p in pin_functions:
        fn=str(p.function or "").upper()
        if any(t in fn for t in ("I2C","SPI","UART","CAN","USB")) and p.net_id not in protocol_nets:
            out.append(TopologyFinding("INTERFACE_PIN_WITHOUT_PROTOCOL","warning",f"{p.connector_id}:{p.pin}",fn))
    return TopologyCoherenceReport(sorted(out,key=lambda x:(x.severity,x.code,x.subject)))
