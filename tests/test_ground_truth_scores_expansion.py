from photonx_eda_pcb.ground_truth.scores import precision_recall
def test_score():
    s=precision_recall({'a','b'},{'b','c'}); assert s['precision']==0.5 and s['recall']==0.5
