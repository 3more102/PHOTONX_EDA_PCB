from .status import status_rank
def compatibility_score(matrix):
    if not matrix.entries:return 0.0
    return round(sum(status_rank(e.status)/3 for e in matrix.entries)/len(matrix.entries),6)
