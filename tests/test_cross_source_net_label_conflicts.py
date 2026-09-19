from types import SimpleNamespace

from photonx_eda_pcb.cross_source_validation import compare_net_labels


def test_compare_net_labels_preserves_set_membership_behavior():
    issues = compare_net_labels({"N1"}, {"N1": "GND", "N2": "VCC"})
    assert issues == [
        {
            "code": "NET_SOURCE_MISSING_PHYSICAL",
            "net_id": "N2",
            "label": "VCC",
        }
    ]


def test_compare_net_labels_reports_conflicting_mapping_labels():
    issues = compare_net_labels({"N1": "GND"}, {"N1": "0V"})
    assert issues == [
        {
            "code": "NET_SOURCE_LABEL_CONFLICT",
            "net_id": "N1",
            "physical_label": "GND",
            "semantic_label": "0V",
        }
    ]


def test_compare_net_labels_accepts_net_group_like_mapping_values():
    physical = {"N1": SimpleNamespace(label="GND")}
    assert compare_net_labels(physical, {"N1": "GND"}) == []


def test_compare_net_labels_ignores_unresolved_labels():
    assert compare_net_labels({"N1": None}, {"N1": "GND"}) == []
    assert compare_net_labels({"N1": "GND"}, {"N1": None}) == []


def test_compare_net_labels_output_is_deterministic_by_net_id():
    issues = compare_net_labels({}, {"N10": "A", "N2": "B", "N1": "C"})
    assert [issue["net_id"] for issue in issues] == ["N1", "N10", "N2"]
