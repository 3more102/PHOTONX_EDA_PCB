import tracemalloc
from .model import MemorySample
def measure_peak_memory(name,fn):
    tracemalloc.start()
    try:
        value=fn();current,peak=tracemalloc.get_traced_memory()
    finally:tracemalloc.stop()
    size=len(value) if hasattr(value,"__len__") else None
    return MemorySample(str(name),int(current),int(peak),size)
