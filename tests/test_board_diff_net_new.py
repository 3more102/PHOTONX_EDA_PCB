from photonx_eda_pcb.board_diff.net_diff import net_membership_diff

def test_net_membership_diff():
    d=net_membership_diff({'N1':['a','b']},{'N1':['b','c']})
    assert d['N1']['removed']==['a'] and d['N1']['added']==['c']
