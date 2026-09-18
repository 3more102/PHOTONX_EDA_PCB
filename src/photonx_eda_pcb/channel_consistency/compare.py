from .model import ChannelDelta,ChannelConsistencyReport
def compare_repeated_group(group):
    deltas=[]
    if not group.instances:return ChannelConsistencyReport([],True)
    ref=group.instances[0]
    for inst in group.instances[1:]:
        if inst.fingerprint!=ref.fingerprint:deltas.append(ChannelDelta(group.id,inst.id,"TOPOLOGY_FINGERPRINT_DIFFERENCE",f"{inst.fingerprint} != {ref.fingerprint}"))
        if tuple(inst.differences):deltas.append(ChannelDelta(group.id,inst.id,"INSTANCE_DIFFERENCES",";".join(inst.differences)))
        if abs(float(inst.similarity)-1.0)>.05:deltas.append(ChannelDelta(group.id,inst.id,"LOW_INSTANCE_SIMILARITY",f"{inst.similarity:.6f}"))
    return ChannelConsistencyReport(deltas,not deltas)
