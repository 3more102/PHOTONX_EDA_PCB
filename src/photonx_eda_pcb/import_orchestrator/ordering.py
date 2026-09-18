PRIORITY={"ipc356":10,"gerber":20,"excellon":30,"kicad_pcb":40,"kicad_schematic":50,"csv":60,"json":70,"unknown":99}
def ordered_results(results):return sorted(results,key=lambda r:(PRIORITY.get(r.format,90),r.path))
