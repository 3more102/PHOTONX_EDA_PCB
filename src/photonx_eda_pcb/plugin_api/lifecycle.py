def activate_all(registry,context):
    activated=[]
    for p in registry.plugins():
        p.activate(context);activated.append(p.metadata.name)
    return activated
def deactivate_all(registry,context):
    done=[]
    for p in reversed(registry.plugins()):
        p.deactivate(context);done.append(p.metadata.name)
    return done
