from dataclasses import dataclass
@dataclass(frozen=True)
class Checkpoint:
    stage:str;artifact_names:tuple[str,...];diagnostic_count:int

def create_checkpoint(stage,ctx):return Checkpoint(stage,tuple(sorted(ctx.artifacts)),len(ctx.diagnostics))
