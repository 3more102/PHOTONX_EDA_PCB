def schematic_stats(data):return {"symbols":len(data.get("symbols",[])),"wires":len(data.get("wires",[])),"labels":len(data.get("labels",[])),"global_labels":len(data.get("global_labels",[]))}
