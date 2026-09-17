from ..analysis.board_stats import board_stats
from ..analysis.completeness import completeness_score
from ..analysis.quality import quality_score
from ..checks import run_all_checks
def build_summary(board):
    issues=run_all_checks(board)
    return {"stats":board_stats(board),"completeness":round(completeness_score(board),4),"quality":round(quality_score(board),4),"check_counts":{"error":sum(i.severity=="error" for i in issues),"warning":sum(i.severity=="warning" for i in issues),"info":sum(i.severity=="info" for i in issues)}}
