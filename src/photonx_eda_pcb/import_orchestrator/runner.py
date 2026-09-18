from photonx_eda_pcb.format_detection import detect_format
from .model import ImportResult
def import_one(request,adapters):
    guess=detect_format(request.path,request.text)
    if request.expected_format and guess.format!=request.expected_format:
        return ImportResult(request.path,False,guess.format,None,[f"FORMAT_MISMATCH:{request.expected_format}:{guess.format}"])
    adapter=adapters.resolve(guess)
    if adapter is None:return ImportResult(request.path,False,guess.format,None,["NO_ADAPTER"])
    try:return ImportResult(request.path,True,guess.format,adapter.read(request.path,request.text),[])
    except Exception as exc:return ImportResult(request.path,False,guess.format,None,[f"IMPORT_ERROR:{type(exc).__name__}:{exc}"])
def import_many(requests,adapters):return [import_one(r,adapters) for r in requests]
