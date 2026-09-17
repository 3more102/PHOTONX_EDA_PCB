from dataclasses import dataclass
@dataclass(frozen=True)
class ControlPoint:
    image_x:float; image_y:float; board_x:float; board_y:float
