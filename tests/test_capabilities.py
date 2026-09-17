from photonx_eda_pcb.capabilities import CAPABILITIES

def test_capability_matrix_is_explicit_about_limits():
    statuses={c.name:c.status for c in CAPABILITIES}; assert statuses["Gerber arcs/regions/macros"]=="not_implemented"; assert statuses["Logical net names"]=="not_inferable"; assert statuses["KiCad board export"]=="experimental"
