from status import Status
from typing import List
from enum import Enum
from db.base import DB
class DamageType(Enum):
    FIRE = "fire"
    COLD = 'cold'
    THUNDER = 'thunder'
    LIGHTNING = 'lightning'
    FORCE = "force"

    BLUDGEONING = 'bludgeoning'
    PIERCING = 'piercing'
    SLASHING = 'slashing'

    ACID = "acid"
    POISON = 'poison'

    RADIANT = 'radiant'
    NECROTIC = 'necrotic'
    PSYCHIC = 'psychic'

    HEALING = 'healing'
    
    VARIES = "varies"



class Spell:
    name: str
    level: int
    effects: list[Status]
    damage: int
    damage_type: DamageType
    cast_range: int
    only_visible_target: bool
    caster: 
    
    def is_can_cast_on(self, target: int):
        pass

    def cast_on(self, target: int ):
        pass


class SpellList:
    max_amount: int #how many spells you can use in max
    spells: List[Spell]

    def set_max(self, value: int) -> None:
        self.max_amount = value

    def new_spell(self, name) -> None:

        self.spells.append(name) #find a way to find spells

    def get_names(self) -> List[str]:
        return [spell.name for spell in self.spells]
    
    def get(self, name) -> Spell:
        return self.spells[name]