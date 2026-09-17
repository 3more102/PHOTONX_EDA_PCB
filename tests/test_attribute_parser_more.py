from photonx_eda_pcb.parsers.common.attributes import parse_attribute_fields
from photonx_eda_pcb.parsers.gerber_parts.attributes import parse_x2_attribute
def test_fields(): assert parse_attribute_fields('%TF.FileFunction,Copper,L1,Top*%')[1][0]=='Copper'
def test_x2(): assert parse_x2_attribute('%TA.AperFunction,Conductor*%')['values']==['Conductor']
