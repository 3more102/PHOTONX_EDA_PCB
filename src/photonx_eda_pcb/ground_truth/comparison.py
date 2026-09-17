from .counts import board_counts
def compare_board_truth(board,truth):
    observed=board_counts(board); diffs={k:(truth.object_counts.get(k),observed.get(k)) for k in truth.object_counts if truth.object_counts.get(k)!=observed.get(k)}
    return {'passed':not diffs,'count_differences':diffs,'observed_counts':observed}
