from .model import LengthGroup
def build_length_groups(buses=(),diff_pairs=(),lengths=None):
    lengths=lengths or {};out=[]
    for b in buses:
        vals=[float(lengths[n]) for n in b.net_ids if n in lengths]
        target=sum(vals)/len(vals) if vals else None
        tol=max(.1,target*.03) if target is not None else None
        out.append(LengthGroup("bus:"+b.name,tuple(b.net_ids),target,tol,"bus",b.confidence))
    for p in diff_pairs:
        nets=(p.positive_net,p.negative_net);vals=[float(lengths[n]) for n in nets if n in lengths]
        target=sum(vals)/len(vals) if len(vals)==2 else None
        tol=max(.05,target*.01) if target is not None else None
        out.append(LengthGroup("diff:"+p.positive_net+":"+p.negative_net,nets,target,tol,"differential",p.confidence))
    return sorted(out,key=lambda x:(x.kind,x.name))
