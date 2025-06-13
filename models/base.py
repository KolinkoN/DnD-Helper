from abc import ABC, abstractmethod
from enum import Enum
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

class Entity(ABC):

    current_hp: int
    max_hp: int

    name: str
    entity_type: str
