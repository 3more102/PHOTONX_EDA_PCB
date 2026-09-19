from photonx_eda_pcb.analysis.provenance_metrics import evidence_count, source_coverage
from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.models import BoardModel, CopperRegion, Point
from photonx_eda_pcb.provenance import Evidence, Provenance, SourceRef


def _source(path: str) -> Provenance:
    return Provenance([SourceRef(path, 1, "source")], [])


def test_routes_and_regions_contribute_to_source_coverage():
    region = CopperRegion(
        "R1",
        (
            Point(0.0, 0.0),
            Point(1.0, 0.0),
            Point(1.0, 1.0),
            Point(0.0, 0.0),
        ),
        "F.Cu",
        provenance=_source("top.gbr"),
    )
    route = RoutedPath(
        "ROUTE1",
        ((0.0, 0.0), (1.0, 0.0)),
        0.5,
    )

    assert source_coverage(BoardModel(regions=[region], routes=[route])) == 0.5


def test_route_and_region_evidence_is_counted():
    region = CopperRegion(
        "R1",
        (
            Point(0.0, 0.0),
            Point(1.0, 0.0),
            Point(1.0, 1.0),
            Point(0.0, 0.0),
        ),
        "F.Cu",
        provenance=Provenance(
            [],
            [Evidence("region", "region evidence", 1.0)],
        ),
    )
    route = RoutedPath(
        "ROUTE1",
        ((0.0, 0.0), (1.0, 0.0)),
        0.5,
        provenance=Provenance(
            [],
            [
                Evidence("route", "route evidence 1", 1.0),
                Evidence("route", "route evidence 2", 0.8),
            ],
        ),
    )

    assert evidence_count(BoardModel(regions=[region], routes=[route])) == 3
