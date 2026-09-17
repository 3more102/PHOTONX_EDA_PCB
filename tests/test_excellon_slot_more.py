import pytest
from photonx_eda_pcb.parsers.excellon_parts.slots import parse_slot_command
def test_slot(): assert parse_slot_command('G85X1Y2X3Y4')==('1','2','3','4')
def test_bad_slot():
 with pytest.raises(ValueError): parse_slot_command('G85X1Y2')
