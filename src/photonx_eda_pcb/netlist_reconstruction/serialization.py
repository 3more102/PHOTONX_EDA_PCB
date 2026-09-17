import json

def netlist_to_dict(netlist):
    return {'nets':{k:[{'component_id':c.component_id,'pin_id':c.pin_id} for c in v] for k,v in sorted(netlist.nets.items())},'labels':dict(sorted(netlist.labels.items()))}

def netlist_json(netlist):return json.dumps(netlist_to_dict(netlist),sort_keys=True,separators=(',',':'))
