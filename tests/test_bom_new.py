from photonx_eda_pcb.bom import read_bom_csv
from photonx_eda_pcb.bom.index import by_reference
from photonx_eda_pcb.bom.validation import validate_bom
def test_bom_ingestion():
    items=read_bom_csv('References,Value,Footprint,Quantity\nR1 R2,330R,Axial,2\nLED1,RED,LED_D5,1\n')
    index=by_reference(items)
    assert index['R1'].value=='330R' and index['LED1'].footprint=='LED_D5'
    assert not validate_bom(items)
