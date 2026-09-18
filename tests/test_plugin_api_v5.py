from photonx_eda_pcb.plugin_api import PluginMetadata,PluginRegistry
from photonx_eda_pcb.plugin_api.base import PhotonxPlugin
from photonx_eda_pcb.plugin_api.validation import validate_plugin
class P(PhotonxPlugin):
    metadata=PluginMetadata("p","1.0",1,("parser","validator"))
def test_plugin_registry():
    r=PluginRegistry();p=P();r.register(p)
    assert r.names()==["p"] and validate_plugin(p)==[]
