def schematic_confidence(board):
    if not board.components or not board.nets:return 0.0
    c=sum(x.confidence for x in board.components)/len(board.components); n=sum(x.confidence for x in board.nets)/len(board.nets)
    return max(0.0,min(1.0,0.5*c+0.5*n))
