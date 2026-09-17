from .common import CommandResult
def manifest_summary(manifest:dict):
    files=manifest.get('files',[]); hashes=manifest.get('sha256',{})
    return CommandResult(0,'manifest inspected',{'files':len(files),'hashes':len(hashes),'root':manifest.get('root')})
