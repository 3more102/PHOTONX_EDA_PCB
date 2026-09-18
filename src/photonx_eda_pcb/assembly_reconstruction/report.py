def assembly_report(assembly):
    return [{"reference":c.reference,"x":c.center[0],"y":c.center[1],"rotation":c.rotation,"side":c.side,"footprint":c.footprint,"value":c.value,"confidence":c.confidence} for c in assembly.components]
