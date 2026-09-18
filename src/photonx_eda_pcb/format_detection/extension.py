EXTENSIONS={".gbr":"gerber",".ger":"gerber",".pho":"gerber",".drl":"excellon",".xln":"excellon",".ipc":"ipc356",".356":"ipc356",".kicad_pcb":"kicad_pcb",".kicad_sch":"kicad_schematic",".csv":"csv",".json":"json"}
def extension_guess(path):
    p=str(path).lower()
    for ext,fmt in sorted(EXTENSIONS.items(),key=lambda x:-len(x[0])):
        if p.endswith(ext):return fmt
    return None
