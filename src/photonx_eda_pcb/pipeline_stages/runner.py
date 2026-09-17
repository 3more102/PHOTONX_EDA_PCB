def run_pipeline(ctx,stages,stop_on_error=True):
    results=[]
    for stage in stages:
        missing=[x for x in stage.requires if x not in ctx.artifacts and x not in ctx.inputs]
        if missing:
            r={'severity':'error','code':'PIPELINE_REQUIREMENT_MISSING','stage':stage.name,'missing':missing};ctx.diagnostics.append(r);results.append((stage.name,False));
            if stop_on_error:break
            continue
        result=stage.run(ctx);results.append(result)
        if hasattr(result,'diagnostics'):ctx.diagnostics.extend(result.diagnostics)
        if stop_on_error and hasattr(result,'ok') and not result.ok:break
    return results
