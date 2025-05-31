import json

class Champion:
    def __init__(self, name, role, faction):
        self.name = name
        self.role = role
        self.faction = faction

    def toJson(self):
        return json.dumps({
            'name': self.name,
            'role': self.role,
            'faction': self.faction
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
    def __init__(self, demon_lord, hydra, waves, chimera, amius, chimera_trials, sintranos_hard_stages):
        self.demon_lord = demon_lord
        self.hydra = hydra
        self.waves = waves
        self.chimera = chimera
        self.amius = amius
        self.chimera_trials = chimera_trials
        self.sintranos_hard_stages = sintranos_hard_stages

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