from .model import FormatGuess
from .extension import extension_guess
from .content import content_hints
def detect_format(path="",text=""):
    scores={};reasons={}
    ext=extension_guess(path)
    if ext:scores[ext]=scores.get(ext,0)+.45;reasons.setdefault(ext,[]).append("extension")
    for fmt,score,reason in content_hints(text):
        scores[fmt]=max(scores.get(fmt,0),score);reasons.setdefault(fmt,[]).append(reason)
    if not scores:return FormatGuess("unknown",0.0,())
    fmt=max(scores,key=lambda k:(scores[k],k))
    confidence=min(1.0,scores[fmt]+(.1 if ext==fmt and any(r!="extension" for r in reasons[fmt]) else 0))
    return FormatGuess(fmt,round(confidence,12),tuple(reasons[fmt]))
