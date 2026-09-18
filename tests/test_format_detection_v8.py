from photonx_eda_pcb.format_detection import detect_format,validate_guess
def test_detect_gerber_from_content_and_extension():
    g=detect_format("top.gbr","%FSLAX24Y24*%\n%MOMM*%\nM02*")
    assert g.format=="gerber" and g.confidence>=.8 and validate_guess(g)==[]
def test_detect_kicad_schematic():
    assert detect_format("x.kicad_sch","(kicad_sch (version 20240101))").format=="kicad_schematic"
