EXTENSIONS = {
    ".gbr": "gerber",
    ".ger": "gerber",
    ".pho": "gerber",
    ".art": "gerber",
    ".gtl": "gerber",
    ".gbl": "gerber",
    ".gts": "gerber",
    ".gbs": "gerber",
    ".gto": "gerber",
    ".gbo": "gerber",
    ".gtp": "gerber",
    ".gbp": "gerber",
    ".gm1": "gerber",
    ".gko": "gerber",
    ".cmp": "gerber",
    ".sol": "gerber",
    ".drl": "excellon",
    ".xln": "excellon",
    ".xnc": "excellon",
    ".exc": "excellon",
    ".tap": "excellon",
    ".drd": "excellon",
    ".ipc": "ipc356",
    ".356": "ipc356",
    ".kicad_pcb": "kicad_pcb",
    ".kicad_sch": "kicad_schematic",
    ".csv": "csv",
    ".json": "json",
}


def extension_guess(path):
    p = str(path).lower()
    for ext, fmt in sorted(EXTENSIONS.items(), key=lambda x: -len(x[0])):
        if p.endswith(ext):
            return fmt
    return None
