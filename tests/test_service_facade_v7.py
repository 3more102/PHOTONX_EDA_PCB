from photonx_eda_pcb.service_facade import ServiceContainer
from photonx_eda_pcb.service_facade.query_service import QueryService
def test_service_container_and_query_service():
    c=ServiceContainer();q=c.register("query",QueryService())
    assert c.names()==["query"]
    query=q.parse("width>0.2")
    assert q.execute([{"width":.1},{"width":.3}],query)==[{"width":.3}]
