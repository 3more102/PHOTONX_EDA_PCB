def run_pipeline(context,stages):
    for stage in stages:
        missing=[k for k in getattr(stage,"requires",()) if k not in context.artifacts and k not in context.inputs]
        if missing:
            context.diagnostics.append(f"STAGE_MISSING:{stage.name}:{','.join(missing)}")
            continue
        try:
            produced=stage.fn(context)
            if isinstance(produced,dict):context.artifacts.update(produced)
        except Exception as exc:
            context.diagnostics.append(f"STAGE_ERROR:{stage.name}:{type(exc).__name__}:{exc}")
    return context
