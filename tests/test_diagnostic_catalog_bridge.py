from photonx_eda_pcb.diagnostic_catalog import default_catalog
from photonx_eda_pcb.diagnostics_ext import (
    definition_for,
    is_cataloged,
    message_for,
    uncataloged_codes,
)


def test_diagnostics_ext_uses_rich_default_catalog():
    definition = definition_for("UNKNOWN_LAYER")
    assert definition is not None
    assert definition.severity == "warning"
    assert "layer" in message_for("UNKNOWN_LAYER").lower()
    assert is_cataloged("EXCELLON_ROUTE_UNTERMINATED")


def test_unknown_diagnostic_fallback_preserves_machine_code():
    code = "VENDOR_EXTENSION_NOT_CATALOGED"
    assert message_for(code) == f"Unknown diagnostic code: {code}."
    assert uncataloged_codes(
        ["UNKNOWN_LAYER", code, code, "EXCELLON_ROUTE_UNTERMINATED"]
    ) == (code,)


def test_default_catalog_covers_preflight_parser_blockers():
    catalog = default_catalog()
    expected = {
        "UNKNOWN_LAYER",
        "PARSER_FAILURE",
        "GERBER_UNITS_UNDECLARED",
        "CONFLICTING_GERBER_UNITS",
        "GERBER_STEP_REPEAT_LIMIT",
        "MALFORMED_EXCELLON_ROUTE",
        "EXCELLON_ROUTE_STATE",
        "EXCELLON_ROUTE_EMPTY",
        "EXCELLON_ROUTE_UNTERMINATED",
        "EXCELLON_ROUTE_ARC_INVALID",
        "EXCELLON_UNITS_UNDECLARED",
    }
    assert catalog.unknown_codes(expected) == ()
