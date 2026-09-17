from .stage import StageResult
def inference_stage(ctx):
    fn=ctx.inputs.get('inference_engine',lambda x:[]);value=fn(ctx.get('connectivity'));ctx.put('inferences',value)
    return StageResult('inference',True,('inferences',),metadata={'count':len(value) if hasattr(value,'__len__') else None})
