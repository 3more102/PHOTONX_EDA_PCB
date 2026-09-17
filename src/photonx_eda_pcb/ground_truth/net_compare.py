from .scores import precision_recall
def compare_net_members(predicted,truth):
    return precision_recall(set(predicted),set(truth))
