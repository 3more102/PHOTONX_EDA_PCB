from photonx_eda_pcb.parsers.excellon_parts.tool_table import parse_tool_definition
from photonx_eda_pcb.parsers.excellon_parts.commands import classify_excellon_command
from photonx_eda_pcb.parsers.excellon_parts.units import parse_excellon_units
def test_tool(): assert parse_tool_definition('T01C0.800').diameter==0.8
def test_command(): assert classify_excellon_command('M48')=='header_begin'
def test_units(): assert parse_excellon_units('INCH,TZ')['units']=='inch'
