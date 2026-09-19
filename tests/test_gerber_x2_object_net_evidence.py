from pathlib import Path

import networkx as nx
from photonx_eda_pcb.connectivity.nets import assign_physical_nets
from photonx_eda_pcb.models import BoardModel, Point, Track
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.provenance import Evidence, Provenance, SourceRef


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(body, encoding="utf-8")
    return path


def _net_names(obj) -> list[str]:
    return [
        item.detail
        for item in obj.provenance.evidence
        if item.kind == "gerber_x2_net_name"
    ]


def _net_provenance(name: str) -> Provenance:
    source = SourceRef("source.gbr", 7, f"%TO.N,{name}*%")
    return Provenance(
        [source],
        [Evidence("gerber_x2_net_name", name, 1.0, source)],
    )


def test_to_n_is_snapshotted_on_created_objects_and_td_is_not_retroactive(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "%TO.N,CLK*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%TD.N*%\n"
        "X020000Y000000D02*\n"
        "X030000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 2
    assert _net_names(result.tracks[0]) == ["CLK"]
    assert _net_names(result.tracks[1]) == []
    assert any(
        item.kind == "gerber_x2_object_attribute"
        and "name=.N" in item.detail
        for item in result.tracks[0].provenance.evidence
    )


def test_to_n_update_affects_only_subsequent_objects(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "%TO.N,CLK*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%TO.N,DATA*%\n"
        "X020000Y000000D02*\n"
        "X030000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert _net_names(result.tracks[0]) == ["CLK"]
    assert _net_names(result.tracks[1]) == ["DATA"]


def test_physical_net_uses_consistent_x2_net_name():
    first = Track(
        "T1",
        Point(0, 0),
        Point(1, 0),
        0.2,
        "F.Cu",
        provenance=_net_provenance("CLK"),
    )
    second = Track("T2", Point(1, 0), Point(2, 0), 0.2, "F.Cu")
    board = BoardModel(tracks=[first, second])
    graph = nx.Graph()
    graph.add_edge("T1", "T2")

    nets = assign_physical_nets(board, graph)

    assert nets[0].label == "CLK"
    assert any(
        item.kind == "gerber_x2_net_label" and item.detail == "name=CLK"
        for item in nets[0].provenance.evidence
    )


def test_conflicting_x2_net_names_remain_unresolved():
    first = Track(
        "T1",
        Point(0, 0),
        Point(1, 0),
        0.2,
        "F.Cu",
        provenance=_net_provenance("CLK"),
    )
    second = Track(
        "T2",
        Point(1, 0),
        Point(2, 0),
        0.2,
        "F.Cu",
        provenance=_net_provenance("DATA"),
    )
    board = BoardModel(tracks=[first, second])
    graph = nx.Graph()
    graph.add_edge("T1", "T2")

    nets = assign_physical_nets(board, graph)

    assert nets[0].label is None
    conflicts = [
        item
        for item in nets[0].provenance.evidence
        if item.kind == "gerber_x2_net_name_conflict"
    ]
    assert len(conflicts) == 1
    assert conflicts[0].detail == "names=['CLK', 'DATA']"


def test_empty_x2_net_name_preserves_explicit_no_net_without_label():
    track = Track(
        "T1",
        Point(0, 0),
        Point(1, 0),
        0.2,
        "F.Cu",
        provenance=_net_provenance(""),
    )
    board = BoardModel(tracks=[track])
    graph = nx.Graph()
    graph.add_node("T1")

    nets = assign_physical_nets(board, graph)

    assert nets[0].label is None
    assert any(
        item.kind == "gerber_x2_no_net"
        for item in nets[0].provenance.evidence
    )


def test_reserved_nc_name_is_preserved_without_becoming_unique_label():
    track = Track(
        "T1",
        Point(0, 0),
        Point(1, 0),
        0.2,
        "F.Cu",
        provenance=_net_provenance("N/C"),
    )
    board = BoardModel(tracks=[track])
    graph = nx.Graph()
    graph.add_node("T1")

    nets = assign_physical_nets(board, graph)

    assert nets[0].label is None
    assert any(
        item.kind == "gerber_x2_reserved_nc"
        for item in nets[0].provenance.evidence
    )


def test_duplicate_source_net_name_across_physical_groups_stays_unresolved():
    first = Track(
        "T1",
        Point(0, 0),
        Point(1, 0),
        0.2,
        "F.Cu",
        provenance=_net_provenance("CLK"),
    )
    second = Track(
        "T2",
        Point(10, 0),
        Point(11, 0),
        0.2,
        "F.Cu",
        provenance=_net_provenance("CLK"),
    )
    board = BoardModel(tracks=[first, second])
    graph = nx.Graph()
    graph.add_nodes_from(["T1", "T2"])

    nets = assign_physical_nets(board, graph)

    assert [net.label for net in nets] == [None, None]
    assert all(
        any(
            item.kind == "gerber_x2_duplicate_net_label"
            for item in net.provenance.evidence
        )
        for net in nets
    )
