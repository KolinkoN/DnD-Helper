from dataclasses import dataclass, field
from typing import List, Optional
# from .coords import Coords
from math import sqrt
FIELD_SIZE: int = 10
def gen_field(size) -> List[List[int]]:
    return [[0 for _ in range(size)] for _ in range(size)]

from dataclasses import dataclass

@dataclass
class Coords:
    x: int
    y: int

class BattleFieldCalc:

    @staticmethod
    def calc_distance(point_1: Coords, point_2: Coords):
        x = (point_1.x - point_2.x) ** 2
        y = (point_1.y - point_2.y) ** 2
        return sqrt(x+y)


@dataclass
class BattleField:
    name: str
    size: Optional[int] = FIELD_SIZE
    field: Optional[List[List[int]]] = field(init=False)

    def __post_init__(self):
        self.field = gen_field(self.size)
    
    def is_point_busy(self, coords: Coords) -> bool:
        return self.field[coords.y][coords.x] != 0
    
    #target should be id
    def move_on_field(self, target: int, coords: Coords):
        if self.is_point_busy(coords):
            return #return some error, like point is busy

        target_coords = self.get_target_coord(target)

        if coords == target_coords:
            return #return some error, like you cant move to your current pos
        
        self.__put_on_pos(coords, 0)
        self.__put_on_pos(target_coords, target)


    def __put_on_pos(self, coords: Coords, value: int):
        self.field[coords.y][coords.x] = value
    
    def get_target_coord(self, target: int) -> Coords:
        for y in range(self.size):
            if target in self.field[y]:
                x = self.field[y].index(target)
                return Coords(x,y)

    

a = Coords(5,2)
b = Coords(5,10)
my_field = BattleField("test")
distance = my_field.calc_distance(a, b)
print(distance)