from photonx_eda_pcb.format_detection import detect_format, validate_guess


def test_detect_gerber_from_content_and_extension():
    guess = detect_format("top.gbr", "%FSLAX24Y24*%\n%MOMM*%\nM02*")
    assert guess.format == "gerber"
    assert guess.confidence >= .8
    assert validate_guess(guess) == []


def test_detect_kicad_schematic():
    assert (
        detect_format("x.kicad_sch", "(kicad_sch (version 20240101))").format
        == "kicad_schematic"
    )


def test_detect_headerless_excellon_uses_ascii_decimal_grammar():
    guess = detect_format("mystery", "T01C.8\nX001250Y-002500\n")
    assert guess.format == "excellon"
    assert guess.confidence == .72
    assert guess.reasons == ("excellon_tool_coordinate_shape",)


def test_detect_headerless_excellon_accepts_decimal_edge_forms():
    guess = detect_format("mystery", "T01C1.\nX.5Y1.\n")
    assert guess.format == "excellon"


def test_detect_headerless_excellon_accepts_y_only_coordinate():
    guess = detect_format("mystery", "T01C0.8\nY-1.25\n")
    assert guess.format == "excellon"


def test_detect_headerless_excellon_rejects_non_ascii_tool_digits():
    guess = detect_format("mystery", "T٠١C0.8\nX123Y456\n")
    assert guess.format == "unknown"


def test_detect_headerless_excellon_rejects_non_ascii_coordinate_digits():
    guess = detect_format("mystery", "T01C0.8\nX١٢٣Y456\n")
    assert guess.format == "unknown"


def test_detect_headerless_excellon_rejects_malformed_decimal_tokens():
    guess = detect_format("mystery", "T01C1..0\nX1..2Y3\n")
    assert guess.format == "unknown"


def test_detect_headerless_excellon_does_not_widen_coordinate_order():
    guess = detect_format("mystery", "T01C0.8\nY1X2\n")
    assert guess.format == "unknown"
