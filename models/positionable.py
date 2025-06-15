from typing import Protocol
from models.coords import Coords

class Positionable(Protocol):
    def get_position(self) -> Coords: ...