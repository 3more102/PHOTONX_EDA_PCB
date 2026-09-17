from pathlib import Path
from ..reporting.csv_tables import nets_csv,components_csv
def export_csv_tables(board,directory:str|Path)->list[Path]:
    d=Path(directory); d.mkdir(parents=True,exist_ok=True); a=d/"nets.csv"; b=d/"components.csv"; a.write_text(nets_csv(board),encoding="utf-8"); b.write_text(components_csv(board),encoding="utf-8"); return [a,b]
