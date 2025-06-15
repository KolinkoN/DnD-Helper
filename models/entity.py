from models.base import BaseEntity
from typing import List
from spell import Spell
from models.coords import Coords

class Entity(BaseEntity):
    spells: List[Spell]


    def get_position(self) -> Coords:
        return self.position
    # def cast_spell(spell: )

    def take_damage(self):
        return super().take_damage()

    def heal(self):
        return super().heal()
    
    def move_to(self, postion):
        return super().move_to()