from .model import ProtocolCandidate
from .signatures import SIGNATURES
from .labels import normalized_labels
def detect_protocols(labels):
    n=normalized_labels(labels);out=[]
    for proto,(tokens,base) in SIGNATURES.items():
        matched=[]
        for token in tokens:
            t=token.replace("_","").upper()
            ids=[nid for nid,label in n.items() if t in label]
            if ids:matched.append(ids[0])
        if len(matched)==len(tokens):out.append(ProtocolCandidate(proto,tuple(matched),base,("net_labels",)))
        elif len(matched)>=max(1,len(tokens)-1):out.append(ProtocolCandidate(proto,tuple(matched),round(base*.55,12),("partial_net_labels",)))
    return sorted(out,key=lambda x:(-x.confidence,x.protocol))
