from .common import CommandResult
def inspect_board(board):
    data={k:len(getattr(board,k,[])) for k in ('tracks','pads','drills','outline','nets','components')}
    return CommandResult(0,'board inspection complete',data)
