from photonx_eda_pcb.manufacturing_package.model import PackageAssessment
from photonx_eda_pcb.manufacturing_package_audit import audit_manufacturing_package
def test_package_audit_propagates_blockers():
    a=PackageAssessment({},["outline"],["PACKAGE_MISSING_OUTLINE"],[])
    r=audit_manufacturing_package(a)
    assert not r.passed and "PACKAGE_MISSING_OUTLINE" in r.blockers
