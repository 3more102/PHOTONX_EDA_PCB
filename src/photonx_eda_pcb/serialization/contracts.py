REQUIRED_BOARD_KEYS=("tracks","pads","drills","outline","nets","components","diagnostics","metadata")
def validate_board_mapping(value): return [key for key in REQUIRED_BOARD_KEYS if key not in value]
