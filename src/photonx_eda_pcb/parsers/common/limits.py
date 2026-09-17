from dataclasses import dataclass
@dataclass(frozen=True)
class ParseLimits:
    max_lines:int=1_000_000
    max_line_length:int=65_536
    max_apertures:int=100_000
    max_objects:int=5_000_000
    def check_line(self,line:str,number:int):
        if number>self.max_lines: raise ValueError("input exceeds maximum line count")
        if len(line)>self.max_line_length: raise ValueError("input line exceeds maximum length")
