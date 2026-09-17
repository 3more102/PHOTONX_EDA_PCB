# Staged import pipeline

Input discovery, parsing, normalization, connectivity, inference, validation and export are modeled as explicit stages with declared requirements and outputs. A missing requirement or failed stage produces a diagnostic and can stop the pipeline deterministically.
