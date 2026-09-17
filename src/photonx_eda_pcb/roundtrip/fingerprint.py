import hashlib,json
from .canonicalize import canonical_board_dict
def board_fingerprint(board):return hashlib.sha256(json.dumps(canonical_board_dict(board),sort_keys=True,separators=(',',':')).encode()).hexdigest()
