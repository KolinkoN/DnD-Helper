from dataclasses import dataclass, field
from typing import List, Optional
FIELD_SIZE: int = 10
def gen_field(size) -> List[List[int]]:
    return [[0 for _ in range(size)] for _ in range(size)]

@dataclass
class BattleField:
    name: str
    size: Optional[int] = FIELD_SIZE
    field: Optional[List[List[int]]] = field(init=False)

    def __post_init__(self):
        self.field = gen_field(self.size)
    
    def is_point_busy(self, x: int, y: int) -> bool:
        return self.field[y][x] == 0
    
    #target should be id
    def move_on_field(self, target: int, x:int, y:int):
        if self.is_point_busy(x,y):
            return #return some error, like point is busy

        next_x, next_y = self.get_target_coord(target)

        if (x,y) == (next_x, next_y):
            return #return some error, like you cant move to your current pos
        
        self.field[y][x] = 0
        self.field[next_y][next_x] = target
    
    def get_target_coord(self, target: int) -> tuple[int, int]:
        for y in range(self.size):
            if target in self.field[y]:
                x = self.field[y].index(target)
                return (x,y)


a = BattleField("name")
print(a)