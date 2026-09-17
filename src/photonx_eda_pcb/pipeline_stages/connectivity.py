from .stage import StageResult
def connectivity_stage(ctx):
    solver=ctx.inputs.get('connectivity_solver')
    if solver is None:return StageResult('connectivity',False,diagnostics=({'severity':'error','code':'CONNECTIVITY_SOLVER_MISSING'},))
    value=solver(ctx.get('normalized_geometry',[]));ctx.put('connectivity',value)
    return StageResult('connectivity',True,('connectivity',))
