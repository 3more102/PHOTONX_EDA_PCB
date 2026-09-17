def board_counts(board): return {k:len(getattr(board,k)) for k in ('tracks','pads','drills','outline','nets','components')}
