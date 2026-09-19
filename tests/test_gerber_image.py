import pytest

from photonx_eda_pcb.gerber_image import ImageCompositionStream


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
