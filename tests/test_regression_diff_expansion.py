from photonx_eda_pcb.regression.diff import dict_diff
def test_diff(): assert dict_diff({'a':1},{'a':2})=={'a':(1,2)}
