from photonx_eda_pcb.copper_solver.union_find import UnionFind

def test_union_find_groups_are_deterministic():
    u=UnionFind(['c','a','b','x']);u.union('a','b');u.union('b','c')
    groups=u.groups()
    assert ['a','b','c'] in groups and ['x'] in groups
