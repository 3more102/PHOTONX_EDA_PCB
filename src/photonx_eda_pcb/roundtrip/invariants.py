def board_invariants(board): return {'tracks':len(board.tracks),'pads':len(board.pads),'drills':len(board.drills),'nets':len(board.nets),'components':len(board.components),'outline':len(board.outline)}
def compare_invariants(a,b):
    aa,bb=board_invariants(a),board_invariants(b); return {k:(aa[k],bb[k]) for k in aa if aa[k]!=bb[k]}
