from typing import NamedTuple, Optional, Tuple


class CameraModel(NamedTuple):
    focal_length: float
    resolution: Tuple[float, float]
    cx: Optional[float] = None
    cy: Optional[float] = None

    @property
    def cx_computed(self) -> float:
        return self.cx if self.cx is not None else self.resolution[0] / 2.0

    @property
    def cy_computed(self) -> float:
        return self.cy if self.cy is not None else self.resolution[1] / 2.0
