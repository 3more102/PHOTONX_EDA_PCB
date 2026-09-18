from photonx_eda_pcb.package_catalog.catalog import PackageCatalog
from photonx_eda_pcb.package_catalog.defaults import common_packages
from photonx_eda_pcb.package_catalog import match_package
def test_package_match():
    c=PackageCatalog(common_packages())
    m=match_package(c,pin_count=8,pitch_mm=1.27,mounting="smd")
    assert m[0][1].name=="SOIC-8" and m[0][0]>=.8
