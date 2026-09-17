from .stage import StageResult
def discovery_stage(ctx):
    files=sorted(ctx.inputs.get('files',[]),key=str);ctx.put('discovered_files',files)
    return StageResult('discovery',True,('discovered_files',),metadata={'count':len(files)})
