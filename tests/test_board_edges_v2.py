from photonx_eda_pcb.board_edges import EdgeSegment,assemble_loops,validate_loops
def test_edge_loop_assembly():
    s=[EdgeSegment("a",(0,0),(2,0)),EdgeSegment("b",(2,0),(2,1)),EdgeSegment("c",(2,1),(0,1)),EdgeSegment("d",(0,1),(0,0))]
    loops=assemble_loops(s)
    assert len(loops)==1
    assert validate_loops(loops)==[]
