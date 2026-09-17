from .topology import dangling_nets,high_fanout_nets

def netlist_report(netlist):
    return {'nets':len(netlist.nets),'connections':sum(len(v) for v in netlist.nets.values()),'dangling':dangling_nets(netlist),'high_fanout':high_fanout_nets(netlist)}
