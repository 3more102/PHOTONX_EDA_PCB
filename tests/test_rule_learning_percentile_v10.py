from photonx_eda_pcb.rule_learning.statistics import percentile
def test_percentile():
    assert percentile([1,2,3,4,5],.5)==3
