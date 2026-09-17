from photonx_eda_pcb.parsers.common.coordinates import CoordinateFormat,parse_coordinate
from photonx_eda_pcb.parsers.common.units import normalize_units,to_mm
def test_coord_format(): assert parse_coordinate('123456',CoordinateFormat(2,4))==12.3456
def test_negative_coord(): assert parse_coordinate('-10000',CoordinateFormat(2,4))==-1.0
def test_units(): assert normalize_units('METRIC')=='mm' and to_mm(1,'inch')==25.4
