from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.parsers.excellon import ExcellonParser
def parser_for_case(case):
    if case.format=="gerber":return GerberRS274XParser(case.layer,strict=case.strict)
    if case.format=="excellon":return ExcellonParser(strict=case.strict)
    raise ValueError("unsupported conformance format: "+case.format)
