def governance_matrix(policies,evidence_by_name):
    from .evaluate import evaluate_benchmark
    out=[]
    for p in policies:out.append(evaluate_benchmark(p,**evidence_by_name.get(p.name,{})))
    return out
