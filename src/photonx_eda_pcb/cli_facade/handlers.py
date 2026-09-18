def register_default_handlers(router):
    router.register("capabilities",lambda req,ctx: sorted(getattr(ctx,"capabilities",[]) if ctx is not None else []))
    router.register("services",lambda req,ctx: ctx.services.names() if ctx is not None and getattr(ctx,"services",None) is not None else [])
    router.register("echo",lambda req,ctx: {"args":list(req.args),"options":dict(req.options)})
    return router
