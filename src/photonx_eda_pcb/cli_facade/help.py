def help_text(router):
    lines=["PHOTONX CLI commands:"]+[f"  {name}" for name in router.commands()]
    return "\n".join(lines)
