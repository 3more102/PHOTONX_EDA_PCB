from photonx_eda_pcb.performance_profiles.model import BenchmarkResult,BenchmarkSample
from photonx_eda_pcb.performance_profiles.budget import PerformanceBudget,budget_passed,regression_passed
def test_performance_budget():
    a=BenchmarkResult("x",(BenchmarkSample(.1),),.1,.1,.1);b=BenchmarkResult("x",(BenchmarkSample(.12),),.12,.12,.12)
    budget=PerformanceBudget("x",.2,1.25)
    assert budget_passed(b,budget) and regression_passed(a,b,budget)
