from photonx_eda_pcb.package_catalog.catalog import PackageCatalog
from photonx_eda_pcb.package_catalog.defaults import common_packages
from photonx_eda_pcb.package_catalog.serialize import dumps_catalog,loads_catalog
def test_package_catalog_roundtrip():
    c=PackageCatalog(common_packages())
    assert [x.name for x in loads_catalog(dumps_catalog(c)).all()]==[x.name for x in c.all()]
