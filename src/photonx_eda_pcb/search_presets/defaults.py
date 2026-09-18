from .model import SearchPreset
def default_presets():
    return [SearchPreset("Low confidence","confidence<0.7"),SearchPreset("Unresolved","status==unresolved"),SearchPreset("Power nets","class_name~power"),SearchPreset("Critical findings","severity==critical")]
