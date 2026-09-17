def compare_expected(observed,expected):
    return [f'{k}: expected {v!r}, got {observed.get(k)!r}' for k,v in expected.items() if observed.get(k)!=v]
