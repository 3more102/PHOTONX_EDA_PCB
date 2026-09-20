import pytest

from photonx_eda_pcb.regression_corpus import (
    Corpus,
    CorpusCase,
    CorpusExpectation,
    run_case,
    validate_corpus,
)


def _case(expectation: CorpusExpectation) -> CorpusCase:
    return CorpusCase(
        "unknown-semantics",
        "parser",
        ("board.gbr",),
        expectation,
    )


def test_declared_unknown_observation_is_preserved_but_not_compared():
    case = _case(
        CorpusExpectation(
            {"tracks": 1},
            unknowns=("original_net_names",),
        )
    )

    result = run_case(
        case,
        lambda _: {
            "tracks": 1,
            "original_net_names": ["GND"],
        },
    )

    assert result.passed
    assert result.differences == ()
    assert result.observed == {
        "tracks": 1,
        "original_net_names": ["GND"],
    }
    assert result.ignored_unknowns == ("original_net_names",)


def test_declared_unknown_may_be_absent_without_failing():
    case = _case(
        CorpusExpectation(
            {"tracks": 1},
            unknowns=("original_net_names",),
        )
    )

    result = run_case(case, lambda _: {"tracks": 1})

    assert result.passed
    assert result.differences == ()
    assert result.ignored_unknowns == ()


def test_undeclared_extra_metric_still_fails():
    case = _case(CorpusExpectation({"tracks": 1}))

    result = run_case(
        case,
        lambda _: {
            "tracks": 1,
            "original_net_names": ["GND"],
        },
    )

    assert not result.passed
    assert result.differences == (
        ("unexpected", "original_net_names", None, ["GND"]),
    )


def test_validation_rejects_unknown_expected_metric_conflict():
    corpus = Corpus(
        [
            _case(
                CorpusExpectation(
                    {
                        "tracks": 1,
                        "original_net_names": [],
                    },
                    unknowns=("original_net_names",),
                )
            )
        ]
    )

    assert "CORPUS_UNKNOWN_EXPECTATION_CONFLICT" in validate_corpus(corpus)


def test_validation_rejects_duplicate_unknown_names():
    corpus = Corpus(
        [
            _case(
                CorpusExpectation(
                    {"tracks": 1},
                    unknowns=("plating", "plating"),
                )
            )
        ]
    )

    assert "CORPUS_DUPLICATE_UNKNOWN" in validate_corpus(corpus)


def test_validation_rejects_tolerance_without_expectation():
    corpus = Corpus(
        [
            _case(
                CorpusExpectation(
                    {"tracks": 1},
                    tolerances={"width": 0.01},
                )
            )
        ]
    )

    assert "CORPUS_TOLERANCE_WITHOUT_EXPECTATION" in validate_corpus(corpus)


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        "not-a-number",
    ],
)
def test_validation_rejects_invalid_tolerance(value):
    corpus = Corpus(
        [
            _case(
                CorpusExpectation(
                    {"width": 1.0},
                    tolerances={"width": value},
                )
            )
        ]
    )

    assert "CORPUS_INVALID_TOLERANCE" in validate_corpus(corpus)


def test_validation_keeps_negative_tolerance_diagnostic():
    corpus = Corpus(
        [
            _case(
                CorpusExpectation(
                    {"width": 1.0},
                    tolerances={"width": -0.01},
                )
            )
        ]
    )

    assert "CORPUS_NEGATIVE_TOLERANCE" in validate_corpus(corpus)
