from .model import TestabilityFinding,TestabilityReport
from .coverage import net_test_coverage,exposed_testpoint_fraction
from .access import accessible_testpoints
def analyze_testability(net_ids,testpoints,min_net_coverage=.7):
    items=list(testpoints);accessible=accessible_testpoints(items)
    coverage=net_test_coverage(net_ids,accessible);exposed=exposed_testpoint_fraction(items)
    f=[]
    if coverage<float(min_net_coverage):f.append(TestabilityFinding("LOW_NET_TEST_COVERAGE","warning","board",f"test coverage {coverage:.3f}"))
    for tp in items:
        if not tp.exposed:f.append(TestabilityFinding("TESTPOINT_NOT_EXPOSED","info",tp.object_id,"candidate is not exposed"))
    return TestabilityReport(f,{"net_test_coverage":coverage,"exposed_fraction":exposed,"testpoints":len(items),"accessible_testpoints":len(accessible)})
