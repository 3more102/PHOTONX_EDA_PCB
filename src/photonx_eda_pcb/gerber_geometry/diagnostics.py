from dataclasses import dataclass
@dataclass(frozen=True)
class GeometryDiagnostic: severity:str; code:str; message:str
def unsupported(feature): return GeometryDiagnostic('warning','GERBER_GEOMETRY_UNSUPPORTED',f'geometry feature not implemented: {feature}')
