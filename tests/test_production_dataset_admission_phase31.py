from photonx_eda_pcb.dataset_manifest import DatasetCase,DatasetFile
from photonx_eda_pcb.production_board_validation.admission import dataset_admission


def test_external_board_requires_provenance_metadata():
    c=DatasetCase("real",(DatasetFile("board.gbr","gerber_copper"),),False)
    x=dataset_admission(c)
    assert "EXTERNAL_SOURCE_REQUIRED" in x
    assert "EXTERNAL_LICENSE_REQUIRED" in x
    assert "EXTERNAL_FILE_CHECKSUM_REQUIRED" in x


def test_external_board_rejects_malformed_checksum():
    c=DatasetCase(
        "real",
        (DatasetFile("board.gbr","gerber_copper","abc"),),
        False,
        license="CC0-1.0",
        source="reference-package",
    )
    x=dataset_admission(c)
    assert "EXTERNAL_FILE_CHECKSUM_INVALID" in x
    assert "EXTERNAL_FILE_CHECKSUM_REQUIRED" not in x


def test_external_board_accepts_valid_sha256_metadata():
    c=DatasetCase(
        "real",
        (DatasetFile("board.gbr","gerber_copper","A"*64),),
        False,
        license="CC0-1.0",
        source="reference-package",
    )
    assert dataset_admission(c)==[]
