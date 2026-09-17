from .stage import StageResult
def validation_stage(ctx):
    validators=ctx.inputs.get('validators',[]);issues=[]
    for fn in validators:issues.extend(fn(ctx) or [])
    ctx.put('validation_issues',issues);ok=not any(x.get('severity') in {'error','fatal'} for x in issues if isinstance(x,dict))
    return StageResult('validation',ok,('validation_issues',),tuple(x for x in issues if isinstance(x,dict)))
