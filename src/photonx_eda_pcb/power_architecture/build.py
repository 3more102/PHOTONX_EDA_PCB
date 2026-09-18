from .model import PowerRail,PowerStage,PowerArchitecture
def build_power_architecture(domains=(),regulators=(),dependencies=(),sequences=(),decoupling=()):
    rails={}
    for d in domains:
        for net in d.supply_nets:rails[str(net)]=PowerRail(str(net),d.voltage,tuple(d.components),d.confidence)
    stages=[PowerStage(r.component_id,r.kind,r.input_nets,r.output_nets,r.enable_nets,r.feedback_nets,r.confidence) for r in regulators]
    evidence=[];scores=[]
    if rails:evidence.append("supply_domains");scores.extend(x.confidence for x in rails.values())
    if stages:evidence.append("regulator_candidates");scores.extend(x.confidence for x in stages)
    if dependencies:evidence.append("rail_dependencies")
    if sequences:evidence.append("enable_sequence")
    if decoupling:evidence.append("decoupling_groups");scores.extend(x.confidence for x in decoupling)
    confidence=round(sum(scores)/len(scores),6) if scores else 0.0
    return PowerArchitecture(rails,stages,list(dependencies),list(sequences),list(decoupling),confidence,evidence)
