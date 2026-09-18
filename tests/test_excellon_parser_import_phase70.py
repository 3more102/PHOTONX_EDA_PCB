def test_excellon_parser_imports_after_route_expansion():
    from photonx_eda_pcb.parsers.excellon import ExcellonParser
    assert ExcellonParser is not None
