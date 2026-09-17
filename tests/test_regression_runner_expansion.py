from photonx_eda_pcb.regression.case import RegressionCase
from photonx_eda_pcb.regression.runner import run_case
def test_run():
    c=RegressionCase('x','.',{'pads':2}); r=run_case(c,lambda _: {'pads':2}); assert r.passed
