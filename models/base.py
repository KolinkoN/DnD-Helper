from abc import ABC, abstractmethod
from enum import Enum
from models.coords import Coords
class Races(Enum):
    AARAKOCRA = 'Aarakocra'
    AASIMAR = 'Aasimar'
    AUTOGNOME = 'Autognome'
    ASTRAL_ELF = 'Astral elf'
    BUGBEAR = 'Bugbear'
    VEDALKEN = 'Vedalken'
    VERDAN = 'Verdan'
    GITH = 'Gith'
    GITHZERAI = 'Githzerai'
    GITHYANKI = 'Githyanki'
    GNOME = 'Gnome'
    GOBLIN = 'Goblin'
    GOLIATH = 'Goliath'
    GRUNG = 'Grung'
    DWARF = 'Dwarf'
    GENASI = 'Genasi'
    DRAGONBORN = 'Dragonborn'
    HARENGON = 'Harengon'
    KALASHTAR = 'Kalashtar'
    KENKU = 'Kenku'
    CENTAUR = 'Centaur'
    KOBOLD = 'Kobold'
    LEONIN = 'Leonin'
    LOCATHAH = 'Locathah'
    LIZARDFOLK = 'Lizardfolk'
    MINOTAUR = 'Minotaur'
    ORC = 'Orc'
    HALF_ORC = 'Half-orc'
    HALFLING = 'Halfling'
    HALF_ELF = 'Half-elf'
    SATYR = 'Satyr'
    OWLIN = 'Owlin'
    TABAXI = 'Tabaxi'
    TIEFLING = 'Tiefling'
    TORTLE = 'Tortle'
    TRITON = 'Triton'
    FIRBOLG = 'Firbolg'
    FAIRY = 'Fairy'
    HUMAN = 'Human'
    ELF = 'Elf'
    YUAN_TI_PUREBLOOD = 'Yuan-ti Pureblood'

class BaseEntity(ABC):

    current_hp: int
    max_hp: int

    name: str
    entity_type: Races
    level: int
    armor_class: int
    speed: int
    position: Coords

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def take_damage(self):
        pass

    @abstractmethod
    def move_to(self):
        pass

    @abstractmethod
    def heal(self):
        pass

    



