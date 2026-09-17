from .stage import StageResult
def normalization_stage(ctx):
    fn=ctx.inputs.get('normalizer',lambda x:x);items=[fn(x) for x in ctx.get('parsed_inputs',[])];ctx.put('normalized_geometry',items)
    return StageResult('normalization',True,('normalized_geometry',),metadata={'count':len(items)})
