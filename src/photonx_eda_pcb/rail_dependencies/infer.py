from .model import RailDependency
def infer_rail_dependencies(regulators):
    out=[]
    for r in regulators:
        for a in r.input_nets:
            for b in r.output_nets:
                if a!=b:out.append(RailDependency(a,b,r.component_id,"regulated_by",min(1.0,r.confidence),("regulator_input_output",)))
    return sorted(out,key=lambda x:(x.upstream,x.downstream,x.via_component))
