from .model import DrcIssue
def check_track_widths(board,cfg): return [DrcIssue('error','TRACK_WIDTH_MIN',f'{t.width:.4f} mm below {cfg.min_track_width_mm:.4f} mm',(t.id,)) for t in board.tracks if t.width<cfg.min_track_width_mm]
