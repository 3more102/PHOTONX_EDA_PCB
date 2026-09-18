def regulator_completeness(r):
    fields=[bool(r.input_nets),bool(r.output_nets),bool(r.enable_nets),bool(r.feedback_nets)]
    return round(sum(fields)/len(fields),6)
