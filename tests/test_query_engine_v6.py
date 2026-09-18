from photonx_eda_pcb.query_engine import parse_query,execute_query,validate_query
def test_query_engine():
    items=[{"id":"a","width":.1},{"id":"b","width":.3}]
    q=parse_query("width>=0.2")
    assert [x["id"] for x in execute_query(items,q)]==["b"]
    assert validate_query(q)==[]
