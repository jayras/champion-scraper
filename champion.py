import json
from dataclasses import dataclass
from enum import Enum

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj is None:
            return None
        if isinstance(obj, Enum):
            return obj.value  # Convert Enum to its value
        if hasattr(obj, "toJson"):  # If the object has a `toJson()`, use it
            return obj.toJson()  # Call toJson() without escaping issues
        return super().default(obj)

class FactionWarsRating(Enum):
    GODLIKE = 5
    GREAT = 4
    GOOD = 3
    OK = 2
    BAD = 1

def get_faction_wars_rating(label: str) -> FactionWarsRating:
    mapping = {
        "Godlike": FactionWarsRating.GODLIKE,
        "Great": FactionWarsRating.GREAT,
        "Good": FactionWarsRating.GOOD,
        "OK": FactionWarsRating.OK,
        "Bad": FactionWarsRating.BAD
    }
    return mapping.get(label, None)  # Returns None if label is unknown

@dataclass
class CoreRatings:
    __slots__ = ('demon_lord', 'hydra', 'waves', 'chimera', 'amius', 'chimera_trials', 'sintranos_hard_stages')
    demon_lord: float
    hydra: float
    waves: float
    chimera: float
    amius: float
    chimera_trials: float
    sintranos_hard_stages: float

    def __init__(self, demon_lord=0.0, hydra=0.0, waves=0.0, chimera=0.0, amius=0.0, chimera_trials=0.0, sintranos_hard_stages=0.0):
        self.demon_lord = demon_lord
        self.hydra = hydra
        self.waves = waves
        self.chimera = chimera
        self.amius = amius
        self.chimera_trials = chimera_trials
        self.sintranos_hard_stages = sintranos_hard_stages

    def setRating(self, name, rating):
        if name == 'Demon Lord' or name == "Demon Lord:":
            self.demon_lord = rating
        elif name == 'Hydra' or name == "Hydra:":
            self.hydra = rating
        elif name == 'Waves' or name == "Waves:":
            self.waves = rating
        elif name == 'Chimera' or name == "Chimera:":
            self.chimera = rating
        elif name == 'Amius' or name == "Amius:":
            self.amius = rating
        elif name == 'Chimera Trials' or name == "Chimera Trials:":
            self.chimera_trials = rating
        elif name == 'Sintranos Hard Stages' or name == "Sintranos Hard Stages:":
            self.sintranos_hard_stages = rating
        else:
            print(f"Warning: Unknown core rating name '{name}' with value {rating}.")

    def toJson(self, as_dict=False):
        data = {
            'Demon Lord': self.demon_lord,
            'Hydra': self.hydra,
            'Waves': self.waves,
            'Chimera': self.chimera,
            'Amius': self.amius,
            'Chimera Trials': self.chimera_trials,
            'Sintranos Hard Stages': self.sintranos_hard_stages
        }
        return data if as_dict else json.dumps(data, cls=CustomEncoder, indent=4)
    
    def __str__(self):
        return self.toJson()

@dataclass    
class DungeonRatings:
    __slots__ = ('spider', 'fire_knight', 'dragon', 'ice_golem', 'iron_twins', 'sand_devil', 'shogun_grove')
    spider: float
    fire_knight: float
    dragon: float
    ice_golem: float
    iron_twins: float
    sand_devil: float
    shogun_grove: float

    def __init__(self, spider=0.0, fire_knight=0.0, dragon=0.0, ice_golem=0.0, iron_twins=0.0, sand_devil=0.0, shogun_grove=0.0):
        self.spider = spider
        self.fire_knight = fire_knight
        self.dragon = dragon
        self.ice_golem = ice_golem
        self.iron_twins = iron_twins
        self.sand_devil = sand_devil
        self.shogun_grove = shogun_grove

    def setRating(self, name, rating):
        if name == 'Spider' or name == "Spider:":
            self.spider = rating
        elif name == 'Fire Knight' or name == "Fire Knight:":
            self.fire_knight = rating
        elif name == 'Dragon' or name == "Dragon:":
            self.dragon = rating
        elif name == 'Ice Golem' or name == "Ice Golem:":
            self.ice_golem = rating
        elif name == 'Iron Twins' or name == "Iron Twins:":
            self.iron_twins = rating
        elif name == 'Sand Devil' or name == "Sand Devil:":
            self.sand_devil = rating
        elif name == 'Shogun Grove' or name == "Shogun Grove:":
            self.shogun_grove = rating
        else:
            print(f"Warning: Unknown dungeon rating name '{name}' with value {rating}.")

    def toJson(self, as_dict=False):
        data ={
            'Spider': self.spider,
            'Fire Knight': self.fire_knight,
            'Dragon': self.dragon,
            'Ice Golem': self.ice_golem,
            'Iron Twins': self.iron_twins,
            'Sand Devil': self.sand_devil,
            'Shogun Grove': self.shogun_grove
        }
        return data if as_dict else json.dumps(data, cls=CustomEncoder, indent=4)
    
    def __str__(self):
        return self.toJson()

@dataclass
class HardModeRatings:
    __slots__ = ('spider', 'fire_knight', 'dragon', 'ice_golem')
    spider: float
    fire_knight: float
    dragon: float
    ice_golem: float

    def __init__(self, spider=0.0, fire_knight=0.0, dragon=0.0, ice_golem=0.0):
        self.spider = spider
        self.fire_knight = fire_knight
        self.dragon = dragon
        self.ice_golem = ice_golem

    def setRating(self, name, rating):
        if name == 'Spider' or name == "Spider:":
            self.spider = rating
        elif name == 'Fire Knight' or name == "Fire Knight:":
            self.fire_knight = rating
        elif name == 'Dragon' or name == "Dragon:":
            self.dragon = rating
        elif name == 'Ice Golem' or name == "Ice Golem:":
            self.ice_golem = rating
        else:
            print(f"Warning: Unknown hard mode rating name '{name}' with value {rating}.")

    def toJson(self, as_dict=False):
        data = {
            'Spider': self.spider,
            'Fire Knight': self.fire_knight,
            'Dragon': self.dragon,
            'Ice Golem': self.ice_golem
        }
        return data if as_dict else json.dumps(data, cls=CustomEncoder, indent=4)

    def __str__(self):
        return self.toJson()

@dataclass
class DoomTowerRatings:
    __slots__ = ('magma_dragon', 'nether_spider', 'celestial_griffin', 'dreadhorn', 'scarab_king', 'frost_spider', 'eternal_dragon', 'dark_fae')
    magma_dragon: float
    nether_spider: float
    celestial_griffin: float
    dreadhorn: float
    scarab_king: float
    frost_spider: float
    eternal_dragon: float
    dark_fae: float

    def __init__(self, magma_dragon=0.0, nether_spider=0.0, celestial_griffin=0.0, dreadhorn=0.0, scarab_king=0.0, frost_spider=0.0, eternal_dragon=0.0, dark_fae=0.0):
        self.magma_dragon = magma_dragon
        self.nether_spider = nether_spider
        self.celestial_griffin = celestial_griffin
        self.dreadhorn = dreadhorn
        self.scarab_king = scarab_king
        self.frost_spider = frost_spider
        self.eternal_dragon = eternal_dragon
        self.dark_fae = dark_fae

    def setRating(self, name, rating):
        if name == 'Magma Dragon' or name == "Magma Dragon:":
            self.magma_dragon = rating
        elif name == 'Nether Spider' or name == "Nether Spider:":
            self.nether_spider = rating
        elif name == 'Celestial Griffin' or name == "Celestial Griffin:":
            self.celestial_griffin = rating
        elif name == 'Dreadhorn' or name == "Dreadhorn:":
            self.dreadhorn = rating
        elif name == 'Scarab King' or name == "Scarab King:":
            self.scarab_king = rating
        elif name == 'Frost Spider' or name == "Frost Spider:":
            self.frost_spider = rating
        elif name == 'Eternal Dragon' or name == "Eternal Dragon:":
            self.eternal_dragon = rating
        elif name == 'Dark Fae' or name == "Dark Fae:":
            self.dark_fae = rating
        else:
            print(f"Warning: Unknown doom tower rating name '{name}' with value {rating}.")

    def toJson(self, as_dict=False):
        data = {
            'Magma Dragon': self.magma_dragon,
            'Nether Spider': self.nether_spider,
            'Celestial Griffin': self.celestial_griffin,
            'Dreadhorn': self.dreadhorn,
            'Scarab King': self.scarab_king,
            'Frost Spider': self.frost_spider,
            'Eternal Dragon': self.eternal_dragon,
            'Dark Fae': self.dark_fae
        }
        return data if as_dict else json.dumps(data, cls=CustomEncoder, indent=4)

    def __str__(self):
        return self.toJson()

# @dataclass
# class FactionWarsRatings:
#     __slots__ = ('damage', 'decrease_defence', 'crowd_control', 'turn_meter_control', 'protection_and_support')
#     damage: FactionWarsRating
#     decrease_defence: FactionWarsRating
#     crowd_control: FactionWarsRating
#     turn_meter_control: FactionWarsRating
#     protection_and_support: FactionWarsRating

#     def __init__(self, damage=None, decrease_defence=None, crowd_control=None, turn_meter_control=None, protection_and_support=None):
#         self.damage = damage
#         self.decrease_defence = decrease_defence
#         self.crowd_control = crowd_control
#         self.turn_meter_control = turn_meter_control
#         self.protection_and_support = protection_and_support

#     def setRating(self, name, rating):
#         if name == 'Damage' or name == "Damage:":
#             self.damage = get_faction_wars_rating(rating)
#         elif name == 'Decrease Defence' or name == "Decrease Defence:":
#             self.decrease_defence = get_faction_wars_rating(rating)
#         elif name == 'Crowd Control' or name == "Crowd Control:":
#             self.crowd_control = get_faction_wars_rating(rating)
#         elif name == 'Turn Meter Control' or name == "Turn Meter Control:":
#             self.turn_meter_control = get_faction_wars_rating(rating)
#         elif name == 'Protection and Support' or name == "Protection and Support:":
#         else:
#             print(f"Warning: Unknown faction wars rating name '{name}' with value {rating}.")

#     def toJson(self, as_dict=False):
#         data = {
#             'Damage': self.damage,
#             'Decrease Defence': self.decrease_defence,
#             'Crowd Control': self.crowd_control,
#             'Turn Meter Control': self.turn_meter_control
#         }
#         return data if as_dict else json.dumps(data, cls=CustomEncoder, indent=4)


    def __str__(self):
        return self.toJson()

@dataclass
class ChampionRatings:
    __slots__ = ('overall', 'book', 'core', 'dungeons', 'hard_mode', 'doom_tower')
    overall: float
    book: int
    core: CoreRatings
    dungeons: DungeonRatings
    hard_mode: HardModeRatings
    doom_tower: DoomTowerRatings
    #faction_wars: FactionWarsRatings

    def __init__(self, overall=0.0, book=0, core=None, dungeons=None, hard_mode=None, doom_tower=None, faction_wars=None):
        self.overall = overall
        self.core = core if core is not None else CoreRatings()
        self.dungeons = dungeons if dungeons is not None else DungeonRatings()
        self.hard_mode = hard_mode if hard_mode is not None else HardModeRatings()
        self.doom_tower = doom_tower if doom_tower is not None else DoomTowerRatings()
        #self.faction_wars = faction_wars if faction_wars is not None else FactionWarsRatings()

    def toJson(self, as_dict=False):
        data = {
            'Overall Rating': self.overall,
            'Book Value': self.book,
            'Core Areas': self.core.toJson(as_dict=True),
            'Dungeons': self.dungeons.toJson(as_dict=True),
            'Hard Mode': self.hard_mode.toJson(as_dict=True),
            'Doom Tower': self.doom_tower.toJson(as_dict=True)
        }
        return data if as_dict else json.dumps(data, cls=CustomEncoder, indent=4)
    
    def __str__(self):
        return self.toJson()

@dataclass
class Champion:
    __slots__ = ('name', 'faction', 'affinity', 'rarity', 'ratings')
    name: str
    faction: str
    affinity: str
    rarity: str
    ratings: ChampionRatings

    def __init__(self, name='', faction='', affinity='', rarity='', ratings=None):
        self.name = name
        self.faction = faction
        self.affinity = affinity
        self.rarity = rarity
        self.ratings = ratings if ratings is not None else ChampionRatings()

    def toJson(self, as_dict=False):
        data = {
            'Name': self.name,
            'Faction': self.faction,
            'Affinity': self.affinity,
            'Rarity': self.rarity,
            "Ratings": self.ratings.toJson(as_dict=True)
        }
        return data if as_dict else json.dumps(data, cls=CustomEncoder, indent=4)
    
    def __str__(self):
        return self.toJson()
