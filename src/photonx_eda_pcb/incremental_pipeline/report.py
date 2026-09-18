def incremental_report(states):return [{"stage":s.name,"cached":s.cached,"input_key":s.input_key,"output_key":s.output_key} for s in states]
