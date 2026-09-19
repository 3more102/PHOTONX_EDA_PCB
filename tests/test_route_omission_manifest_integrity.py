from photonx_eda_pcb.exporters.route_omissions import (
    validate_route_omission_manifest,
)


def test_non_mapping_manifest_fails_closed():
    assert validate_route_omission_manifest(None) == [
        "ROUTE_OMISSION_MANIFEST_INVALID"
    ]


def test_string_route_collection_is_rejected_without_iterating_characters():
    issues = validate_route_omission_manifest({
        "omitted_routes": "route-1",
        "reasons": {},
    })
    assert "ROUTE_OMISSION_IDS_INVALID" in issues


def test_invalid_and_unhashable_route_ids_do_not_raise():
    issues = validate_route_omission_manifest({
        "omitted_routes": [["nested"], "", None],
        "reasons": {},
    })
    assert issues == ["ROUTE_OMISSION_ID_INVALID"]


def test_duplicate_route_ids_are_reported_once():
    issues = validate_route_omission_manifest({
        "omitted_routes": ["r1", "r1", "r1"],
        "reasons": {"r1": "KICAD_ARBITRARY_ROUTE_UNSUPPORTED"},
    })
    assert issues == ["ROUTE_OMISSION_DUPLICATE_ID"]


def test_missing_reason_and_orphan_reason_are_both_visible():
    issues = validate_route_omission_manifest({
        "omitted_routes": ["r1"],
        "reasons": {"r2": "KICAD_ARBITRARY_ROUTE_UNSUPPORTED"},
    })
    assert issues == [
        "ROUTE_OMISSION_WITHOUT_REASON",
        "ROUTE_OMISSION_REASON_WITHOUT_ROUTE",
    ]


def test_reason_mapping_shape_and_values_are_validated():
    issues = validate_route_omission_manifest({
        "omitted_routes": ["r1"],
        "reasons": {"r1": ""},
    })
    assert issues == ["ROUTE_OMISSION_REASON_INVALID"]

    issues = validate_route_omission_manifest({
        "omitted_routes": ["r1"],
        "reasons": [],
    })
    assert issues == [
        "ROUTE_OMISSION_REASONS_INVALID",
        "ROUTE_OMISSION_WITHOUT_REASON",
    ]


def test_reason_keys_must_be_nonempty_strings():
    issues = validate_route_omission_manifest({
        "omitted_routes": [],
        "reasons": {1: "KICAD_ARBITRARY_ROUTE_UNSUPPORTED", "": "x"},
    })
    assert issues == ["ROUTE_OMISSION_REASON_ID_INVALID"]


def test_valid_manifest_remains_clean():
    assert validate_route_omission_manifest({
        "omitted_routes": ["r1", "r2"],
        "reasons": {
            "r1": "KICAD_ARBITRARY_ROUTE_UNSUPPORTED",
            "r2": "KICAD_ARBITRARY_ROUTE_UNSUPPORTED",
        },
    }) == []
