from types import SimpleNamespace as NS
from photonx_eda_pcb.validation_rules.geometry_rules import positive_geometry
from photonx_eda_pcb.validation_rules.metadata_rules import metadata_sanity
def test_geometry_detects_width():
 b=NS(tracks=[NS(id='T',width=0)],pads=[],drills=[]); assert positive_geometry(b)[0].code=='TRACK_WIDTH'
def test_metadata_units():
 b=NS(metadata={'units':'yards'}); assert metadata_sanity(b)[0].code=='METADATA_UNITS'
