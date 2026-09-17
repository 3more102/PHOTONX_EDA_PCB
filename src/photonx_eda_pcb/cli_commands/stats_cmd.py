from .common import CommandResult
def board_counts(board):
    data={k:len(getattr(board,k,[])) for k in ('tracks','pads','drills','outline','nets','components','diagnostics')}
    return CommandResult(0,'statistics generated',data)
