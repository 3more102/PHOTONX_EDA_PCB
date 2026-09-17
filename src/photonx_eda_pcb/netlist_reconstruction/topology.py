def net_degree(netlist,net_id):return len(netlist.nets.get(net_id,()))

def dangling_nets(netlist):return sorted(k for k,v in netlist.nets.items() if len(v)<=1)

def high_fanout_nets(netlist,threshold=8):return sorted(k for k,v in netlist.nets.items() if len(v)>=threshold)
