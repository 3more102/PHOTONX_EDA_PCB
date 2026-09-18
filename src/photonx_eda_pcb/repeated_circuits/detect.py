import hashlib
from photonx_eda_pcb.subgraph_fingerprints.similarity import fingerprint_similarity
from photonx_eda_pcb.subgraph_fingerprints.differences import fingerprint_differences
from .candidates import exact_topology_groups
from .instances import instance_members
from .confidence import group_confidence
from .model import CircuitInstance,RepeatedCircuitGroup
def detect_repeated_circuits(fingerprints,min_similarity=.75):
    out=[]
    for group in exact_topology_groups(fingerprints):
        ref=group[0];instances=[];sims=[]
        for f in group:
            sim=fingerprint_similarity(ref,f);sims.append(sim)
            comps,nets=instance_members(f)
            instances.append(CircuitInstance("inst:"+f.seed,f.seed,comps,nets,f.semantic_hash,sim,fingerprint_differences(ref,f)))
        if len(instances)<2 or min(sims)<float(min_similarity):continue
        raw="|".join(x.seed for x in instances)+"|"+ref.topology_hash
        gid="repeat:"+hashlib.sha1(raw.encode()).hexdigest()[:12]
        conf=group_confidence(sims,[x.confidence for x in group])
        ev=["same_topology_hash","subgraph_similarity"]
        if all(not x.differences for x in instances):ev.append("same_semantic_fingerprint")
        out.append(RepeatedCircuitGroup(gid,tuple(instances),ref.topology_hash,round(sum(sims)/len(sims),6),conf,tuple(ev)))
    return sorted(out,key=lambda x:(-len(x.instances),-x.confidence,x.id))
