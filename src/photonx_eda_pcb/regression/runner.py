from .result import RegressionResult
from .expectation import compare_expected
def run_case(case,producer):
    observed=producer(case); failures=compare_expected(observed,case.expected)
    return RegressionResult(case.name,not failures,failures,observed)
