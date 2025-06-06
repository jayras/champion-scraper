import json

class Champion:
    def __init__(self, name, faction, affinity):
        self.name = name
        self.faction = faction
        self.affinity = affinity
        self.champion_ratings = None
    
    def setChampionRatings(self, championRatingsBuiler):
        self.champion_ratings = championRatingsBuiler.build()
        
        return self

    def toJson(self):
        return json.dumps({
            'name': self.name,
            'faction': self.faction,
            'affinity': self.affinity,
            "champion_ratings": self.champion_ratings.toJson() if self.champion_ratings else None
        })
    
    def __str__(self):
        return self.toJson()


class ChampionRatings:
    def __init__(self, overall, core, dungeons, hard_mode, doom_tower, faction_wars):
        self.overall = overall
        self.core = core
        self.dungeons = dungeons
        self.hard_mode = hard_mode
        self.doom_tower = doom_tower
        self.faction_wars = faction_wars

    def toJson(self):
        return json.dumps({
            'Overall Rating': self.overall,
            'Core Areas': self.core.toJson,
            'Dungeons': self.dungeons.toJson,
            'Hard Mode': self.hard_mode.toJson,
            'Doom Tower': self.doom_tower.toJson,
            'Faction Wars': self.faction_wars.toJson
        })
    
    def __str__(self):
        return self.toJson()

class coreRatings:
    def __init__(self):
        self.demon_lord = 0
        self.hydra = 0
        self.waves = 0
        self.chimera = 0
        self.amius = 0
        self.chimera_trials = 0
        self.sintranos_hard_stages = 0

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

    def toJson(self):
        return json.dumps({
            'Demon Lord': self.demon_lord,
            'Hydra': self.hydra,
            'Waves': self.waves,
            'Chimera': self.chimera,
            'Amius': self.amius,
            'Chimera Trials': self.chimera_trials,
            'Sintranos Hard Stages': self.sintranos_hard_stages
        })
    
    def __str__(self):
        return self.toJson()
    
class dungeonRatings:
    def __init__(self):
        self.spider = 0
        self.fire_knight = 0
        self.dragon = 0
        self.ice_golem = 0
        self.iron_twins = 0
        self.sand_devil = 0
        self.shogun_grove = 0
    
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

    def toJson(self):
        return json.dumps({
            'Spider': self.spider,
            'Fire Knight': self.fire_knight,
            'Dragon': self.dragon,
            'Ice Golem': self.ice_golem,
            'Iron Twins': self.iron_twins,
            'Sand Devil': self.sand_devil,
            'Shogun Grove': self.shogun_grove
        })
    def __str__(self):
        return self.toJson()

class hardModeRatings:
    def __init__(self):
        self.spider = 0
        self.fire_knight = 0
        self.dragon = 0
        self.ice_golem = 0

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

    def toJson(self):
        return json.dumps({
            'Spider': self.spider,
            'Fire Knight': self.fire_knight,
            'Dragon': self.dragon,
            'Ice Golem': self.ice_golem
        })

    def __str__(self):
        return self.toJson()

class doomTowerRatings:
    def __init__(self, magna_dragon, nether_spider, celestial_griffin, dreadhorn, scarab_king, frost_spider, eternal_dragon, dark_fae):
        self.magna_dragon = magna_dragon
        self.nether_spider = nether_spider
        self.celestial_griffin = celestial_griffin
        self.dreadhorn = dreadhorn
        self.scarab_king = scarab_king
        self.frost_spider = frost_spider
        self.eternal_dragon = eternal_dragon
        self.dark_fae = dark_fae

    def toJson(self):
        return json.dumps({
            'Magna Dragon': self.magna_dragon,
            'Nether Spider': self.nether_spider,
            'Celestial Griffin': self.celestial_griffin,
            'Dreadhorn': self.dreadhorn,
            'Scarab King': self.scarab_king,
            'Frost Spider': self.frost_spider,
            'Eternal Dragon': self.eternal_dragon,
            'Dark Fae': self.dark_fae
        })

    def __str__(self):
        return self.toJson()

class factionWarsRatings:
    def __init__(self, damage, decrease_defence, crowd_control, turn_meter_control):
        self.damage = damage
        self.decrease_defence = decrease_defence
        self.crowd_control = crowd_control
        self.turn_meter_control = turn_meter_control

    def toJson(self):
        return json.dumps({
            'Damage': self.damage,
            'Decrease Defence': self.decrease_defence,
            'Crowd Control': self.crowd_control,
            'Turn Meter Control': self.turn_meter_control
        })

    def __str__(self):
        return self.toJson()

class ChampionRatingsBuilder:
    def __init__(self):
        self.overall = None
        self.core = None
        self.dungeons = None
        self.hard_mode = None
        self.doom_tower = None
        self.faction_wars = None

    def setOverall(self, overall: float):
        self.overall = overall
        return self

    def setCore(self, core: coreRatings):
        self.core = core
        return self

    def setDungeons(self, dungeons: dungeonRatings):
        self.dungeons = dungeons
        return self

    def setHardMode(self, hard_mode: hardModeRatings):
        self.hard_mode = hard_mode
        return self

    def setDoomTower(self, doom_tower: doomTowerRatings):
        self.doom_tower = doom_tower
        return self

    def setFactionWars(self, faction_wars: factionWarsRatings):
        self.faction_wars = faction_wars
        return self

    def build(self):
        return ChampionRatings(
            overall=self.overall,
            core=self.core,
            dungeons=self.dungeons,
            hard_mode=self.hard_mode,
            doom_tower=self.doom_tower,
            faction_wars=self.faction_wars
        )

def createChampion(name, role, faction):
    return Champion(name, role, faction)

def createChampionRatings(overall, core, dungeons, hard_mode, doom_tower, faction_wars):
    return ChampionRatingsBuilder() \
        .setOverall(overall) \
        .setCore(core) \
        .setDungeons(dungeons) \
        .setHardMode(hard_mode) \
        .setDoomTower(doom_tower) \
        .setFactionWars(faction_wars) \
        .build()

def createCoreRatings(demon_lord, hydra, waves, chimera, amius, chimera_trials, sintranos_hard_stages):
    return coreRatings(
        demon_lord=demon_lord,
        hydra=hydra,
        waves=waves,
        chimera=chimera,
        amius=amius,
        chimera_trials=chimera_trials,
        sintranos_hard_stages=sintranos_hard_stages
    )

def createDungeonRatings(spider, fire_knight, dragon, ice_golem, iron_twins, sand_devil, shogun_grove):
    return dungeonRatings(
        spider=spider,
        fire_knight=fire_knight,
        dragon=dragon,
        ice_golem=ice_golem,
        iron_twins=iron_twins,
        sand_devil=sand_devil,
        shogun_grove=shogun_grove
    )

def createHardModeRatings(spider, fire_knight, dragon, ice_golem):
    return hardModeRatings(
        spider=spider,
        fire_knight=fire_knight,
        dragon=dragon,
        ice_golem=ice_golem
    )

def createDoomTowerRatings(magna_dragon, nether_spider, celestial_griffin, dreadhorn, scarab_king, frost_spider, eternal_dragon, dark_fae):
    return doomTowerRatings(
        magna_dragon=magna_dragon,
        nether_spider=nether_spider,
        celestial_griffin=celestial_griffin,
        dreadhorn=dreadhorn,
        scarab_king=scarab_king,
        frost_spider=frost_spider,
        eternal_dragon=eternal_dragon,
        dark_fae=dark_fae
    )

def createFactionWarsRatings(damage, decrease_defence, crowd_control, turn_meter_control):
    return factionWarsRatings(
        damage=damage,
        decrease_defence=decrease_defence,
        crowd_control=crowd_control,
        turn_meter_control=turn_meter_control
    )
