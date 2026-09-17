from .model import DrcIssue
def check_drills(board,cfg): return [DrcIssue('error','DRILL_MIN',f'{d.diameter:.4f} mm below {cfg.min_drill_mm:.4f} mm',(d.id,)) for d in board.drills if d.diameter<cfg.min_drill_mm]
