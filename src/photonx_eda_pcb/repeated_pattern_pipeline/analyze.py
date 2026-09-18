from photonx_eda_pcb.subgraph_fingerprints import fingerprint_around_component
from photonx_eda_pcb.repeated_circuits import detect_repeated_circuits
from photonx_eda_pcb.repeated_circuits.evidence import evidence_records
from photonx_eda_pcb.repeated_circuits.review import review_items
from photonx_eda_pcb.channel_detection import detect_channels
from photonx_eda_pcb.pattern_library.defaults import default_patterns
from photonx_eda_pcb.pattern_library.library import PatternLibrary
from photonx_eda_pcb.pattern_library.matcher import match_patterns
from .model import RepeatedPatternAnalysis
def analyze_repeated_patterns(graph,seeds,identity_by_id=None,roles_by_net=None,radius=2,pattern_library=None,min_similarity=.75):
    identity_by_id=identity_by_id or {};roles_by_net=roles_by_net or {}
    fps=[fingerprint_around_component(graph,s,radius,identity_by_id,roles_by_net) for s in sorted(map(str,seeds))]
    groups=detect_repeated_circuits(fps,min_similarity)
    channels=detect_channels(groups,identity_by_id,roles_by_net)
    lib=pattern_library or PatternLibrary(default_patterns());matches=[]
    for g in groups:
        for inst in g.instances:
            kinds=[str(getattr(identity_by_id.get(c),"kind","unknown") or "unknown") for c in inst.components]
            roles=sorted({r for n in inst.nets for r in roles_by_net.get(n,())})
            matches.extend(match_patterns(lib,inst.id,kinds,roles))
    return RepeatedPatternAnalysis(fps,groups,channels,matches,evidence_records(groups),review_items(groups))
