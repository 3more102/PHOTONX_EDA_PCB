import pytest
from shapely.geometry import LineString, Polygon, box

from photonx_eda_pcb.gerber_image import (
    ImageCompositionStream,
    ImageOperation,
    canonical_polygon_components,
    compose_polygon_operations,
)


def test_image_composition_stream_preserves_interleaved_order():
    stream = ImageCompositionStream[str]()
    first = stream.append("dark", "dark-a")
    second = stream.append("clear", "clear-a")
    third = stream.append("dark", "dark-b")

    assert [op.sequence for op in stream.operations] == [0, 1, 2]
    assert [op.polarity for op in stream.operations] == ["dark", "clear", "dark"]
    assert [op.geometry for op in stream.operations] == ["dark-a", "clear-a", "dark-b"]
    assert first.sequence < second.sequence < third.sequence


def test_image_composition_stream_is_immutable_to_callers():
    stream = ImageCompositionStream[str]()
    stream.append("dark", "a")
    snapshot = stream.operations
    stream.append("clear", "b")

    assert len(snapshot) == 1
    assert len(stream.operations) == 2


def test_image_composition_stream_rejects_unknown_polarity():
    stream = ImageCompositionStream[str]()
    with pytest.raises(ValueError, match="invalid Gerber image polarity"):
        stream.append("negative", "bad")  # type: ignore[arg-type]


def test_image_composition_stream_clear_resets_sequence():
    stream = ImageCompositionStream[str]()
    stream.append("dark", "a")
    stream.clear()

    assert stream.operations == ()
    assert stream.append("clear", "b").sequence == 0


def test_polygon_composition_applies_clear_in_order_and_allows_dark_refill():
    stream = ImageCompositionStream()
    stream.append("dark", box(0, 0, 10, 10))
    stream.append("clear", box(3, 3, 7, 7))
    stream.append("dark", box(4, 4, 6, 6))

    composed = compose_polygon_operations(stream.operations)
    components = canonical_polygon_components(composed)

    assert composed.area == pytest.approx(88.0)
    assert len(components) == 2
    assert len(components[0].holes) == 1
    assert components[1].holes == ()


def test_polygon_composition_clear_before_dark_is_a_noop():
    stream = ImageCompositionStream()
    stream.append("clear", box(0, 0, 5, 5))
    stream.append("dark", box(0, 0, 10, 10))

    composed = compose_polygon_operations(stream.operations)

    assert composed.area == pytest.approx(100.0)


def test_polygon_composition_can_split_image_into_deterministic_components():
    stream = ImageCompositionStream()
    stream.append("dark", box(0, 0, 10, 10))
    stream.append("clear", box(4, -1, 6, 11))

    composed = compose_polygon_operations(stream.operations)
    components = canonical_polygon_components(composed)

    assert composed.area == pytest.approx(80.0)
    assert len(components) == 2
    assert components[0].shell[0] == (0.0, 0.0)
    assert components[1].shell[0] == (6.0, 0.0)


def test_canonical_components_do_not_depend_on_disjoint_dark_operation_order():
    first = ImageCompositionStream()
    first.append("dark", box(10, 0, 11, 1))
    first.append("dark", box(0, 0, 1, 1))

    second = ImageCompositionStream()
    second.append("dark", box(0, 0, 1, 1))
    second.append("dark", box(10, 0, 11, 1))

    assert canonical_polygon_components(
        compose_polygon_operations(first.operations)
    ) == canonical_polygon_components(compose_polygon_operations(second.operations))


def test_polygon_composition_rejects_non_polygonal_geometry():
    stream = ImageCompositionStream()
    stream.append("dark", LineString([(0, 0), (1, 1)]))

    with pytest.raises(TypeError, match="Polygon or MultiPolygon"):
        compose_polygon_operations(stream.operations)


def test_polygon_composition_rejects_invalid_polygon_geometry():
    bowtie = Polygon([(0, 0), (2, 2), (0, 2), (2, 0), (0, 0)])
    stream = ImageCompositionStream()
    stream.append("dark", bowtie)

    with pytest.raises(ValueError, match="invalid geometry"):
        compose_polygon_operations(stream.operations)


def test_polygon_composition_rejects_sequence_gaps():
    operations = (
        ImageOperation(0, "dark", box(0, 0, 1, 1)),
        ImageOperation(2, "clear", box(0, 0, 0.5, 0.5)),
    )

    with pytest.raises(ValueError, match="contiguous and ordered"):
        compose_polygon_operations(operations)
