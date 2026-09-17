from photonx_eda_pcb.parsers.gerber_parts.aperture import parse_aperture
from photonx_eda_pcb.parsers.gerber_parts.format_spec import parse_format_spec
from photonx_eda_pcb.parsers.gerber_parts.commands import classify_command
def test_aperture():
 a=parse_aperture('%ADD10C,0.500*%'); assert a.code==10 and a.x==0.5
def test_format():
 f=parse_format_spec('%FSLAX24Y24*%'); assert (f.x_integer,f.x_decimal)==(2,4)
def test_classification(): assert classify_command('%LPD*%')=='polarity'
