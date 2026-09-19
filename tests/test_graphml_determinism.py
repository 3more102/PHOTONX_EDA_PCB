from photonx_eda_pcb.exporters.graphml import export_graphml
from photonx_eda_pcb.models import BoardModel, NetGroup


def _board(net_order, member_order):
    members = {
        "N0": ["D", "C"],
        "N1": ["B", "A"],
    }
    nets = [
        NetGroup(net_id, list(reversed(members[net_id])) if member_order == "reverse" else members[net_id], 1.0)
        for net_id in net_order
    ]
    return BoardModel(nets=nets)


def test_graphml_is_stable_across_equivalent_net_and_member_ordering(tmp_path):
    first = tmp_path / "first.graphml"
    second = tmp_path / "second.graphml"

    export_graphml(_board(["N1", "N0"], "reverse"), first)
    export_graphml(_board(["N0", "N1"], "forward"), second)

    assert first.read_bytes() == second.read_bytes()

    text = first.read_text(encoding="utf-8")
    assert 'source="C" target="D"' in text
    assert 'source="A" target="B"' in text
