import pytest
from photonx_eda_pcb.parsers.common.limits import ParseLimits
def test_limits(): ParseLimits(max_lines=2,max_line_length=3).check_line('abc',2)
def test_too_long():
 with pytest.raises(ValueError): ParseLimits(max_line_length=2).check_line('abc',1)
