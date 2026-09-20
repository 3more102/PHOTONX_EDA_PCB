SIGNATURES = [
    {"name": "TWO_PIN_THT", "pad_count": 2, "drilled_min": 0.9, "aspect_min": 1.2},
    {"name": "TWO_PAD_SMD", "pad_count": 2, "drilled_max": 0.1, "aspect_min": 1.2},
    {"name": "SOIC8_LIKE", "pad_count": 8, "drilled_max": 0.1, "aspect_min": 1.2},
    {"name": "DIP8_LIKE", "pad_count": 8, "drilled_min": 0.8, "aspect_min": 1.2},
    {
        "name": "DUAL_ROW_THT_LIKE",
        "pad_count_min": 4,
        "pad_count_max": 64,
        "drilled_min": 0.8,
        "two_row_min": 0.75,
        "symmetry_min": 0.75,
    },
    {
        "name": "DUAL_ROW_SMD_LIKE",
        "pad_count_min": 6,
        "pad_count_max": 64,
        "drilled_max": 0.15,
        "two_row_min": 0.75,
        "symmetry_min": 0.75,
    },
    {
        "name": "GRID_ARRAY_SMD_LIKE",
        "pad_count_min": 9,
        "pad_count_max": 400,
        "drilled_max": 0.15,
        "grid_rows_min": 3,
        "grid_columns_min": 3,
        "grid_occupancy_min": 0.8,
        "symmetry_min": 0.75,
    },
]


def signature_by_name(name):
    return next((item for item in SIGNATURES if item["name"] == name), None)
