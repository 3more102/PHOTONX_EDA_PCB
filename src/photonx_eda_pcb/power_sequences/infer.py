from .model import SequenceConstraint
def infer_power_sequence(regulators,enable_source_by_net=None):
    enable_source_by_net=enable_source_by_net or {};out=[]
    for r in regulators:
        for en in r.enable_nets:
            source=enable_source_by_net.get(en)
            if source:
                for outnet in r.output_nets:
                    if source!=outnet:out.append(SequenceConstraint(str(source),str(outnet),f"enable:{en}",round(min(.9,r.confidence),6),("enable_net_source",)))
    return sorted(out,key=lambda x:(x.before,x.after,x.reason))
