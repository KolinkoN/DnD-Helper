from dataclasses import dataclass, field 
from enum import Enum

class StatusEffects(Enum):
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "defeaned"
    FRIGHTENED = "frightened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapaciated"
    INVISIBLE = "invisible"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    PRONE = "prone"
    RESTRAINED = "restrained"
    STUNNED = "stunned"
    UNCONSCIOUS = "unconscious"

@dataclass
class Status:
    name: str
    effect: StatusEffects
    duration: int

    def revoke_status(self, duration: int):
        self.duration = duration