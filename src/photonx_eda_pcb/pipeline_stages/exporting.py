from .stage import StageResult
def exporting_stage(ctx):
    exporters=ctx.inputs.get('exporters',{});outputs={}
    for name,fn in sorted(exporters.items()):outputs[name]=fn(ctx)
    ctx.put('exports',outputs);return StageResult('exporting',True,('exports',),metadata={'formats':sorted(outputs)})
