from ..models import BoardModel
def component_confidence_mean(board:BoardModel)->float:
    return 0.0 if not board.components else sum(c.confidence for c in board.components)/len(board.components)
def unresolved_components(board:BoardModel,threshold:float=0.5): return [c.id for c in board.components if c.confidence<threshold]
def component_pad_counts(board:BoardModel): return {c.id:len(c.pad_ids) for c in board.components}
