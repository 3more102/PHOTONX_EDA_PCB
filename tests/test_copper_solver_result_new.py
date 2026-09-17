from photonx_eda_pcb.copper_solver.model import ContactEdge
from photonx_eda_pcb.copper_solver.solver import solve_connectivity
from photonx_eda_pcb.copper_solver.stats import solver_stats

def test_solver_connects_edges_and_rejects_self_edge():
    r=solve_connectivity(['a','b','c'],[ContactEdge('a','b',confidence=.9),ContactEdge('c','c')])
    assert ['a','b'] in r.groups and ['c'] in r.groups
    assert solver_stats(r)['edges']==1
    assert r.diagnostics[0]['code']=='SELF_CONTACT_EDGE'
