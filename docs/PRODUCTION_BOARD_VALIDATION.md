# Production Board Validation

Production validation aggregates core model validation, DRC, ERC, provenance coverage, outline/connectivity requirements and release evidence.

External reference boards require source, license and a valid 64-hex SHA-256 checksum for every referenced file before dataset admission. Missing checksums remain distinct from malformed checksum metadata so review tooling can report the correct blocker.

A passing PHOTONX production-validation gate is not electrical certification, fab approval, or proof that unknown design intent has been recovered.
