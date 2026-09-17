from .base import RuleIssue
def valid_drill_plating(board):
    allowed={'unknown','plated','non_plated'}
    return [RuleIssue('warning','DRILL_PLATING_ENUM',f'unexpected plating {d.plating}',d.id) for d in getattr(board,'drills',[]) if d.plating not in allowed]
