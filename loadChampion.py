from bs4 import BeautifulSoup
import os
import champion
import re

def is_numeric(s):
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", s))

def getFactionFromSource(faction_source):
    # Gets faction based on the image source URL:
    # /wp-content/plugins/rsl-assets/assets/factions/shadowkin.png is Shadowkin
    #Warning: Could not determine affinity from source: /wp-content/plugins/rsl-assets/assets/factions/shadowkin.png
    faction_map = {
        "shadowkin": "Shadowkin",
        "sacred-order": "Sacred Order",
        "high-elves": "High Elves",
        "barbarians": "Barbarians",
        "orcs": "Orcs",
        "dwarves": "Dwarves",
        "lizardmen": "Lizardmen",
        "undead-hordes": "Undead Hordes",
        "knight-revenant": "Knight Revenant",
        "dark-elves": "Dark Elves",
        "skinwalkers": "Skinwalkers",
        "ogryn-tribes": "Ogryn Tribes",
        "demonspawn": "Demon Spawn",
        "void": "Void"
    }

    #faction_key = os.path.splitext(os.path.basename(faction_source))[0]
    faction_key = faction_source.rsplit("/", 1)[-1].split(".")[0]

    if faction_key in faction_map:
        return faction_map[faction_key]
    print("Warning: Could not determine faction from source:", faction_source)
    return None

def getAffinityFromSource(affinity_source): 
    # Gets affinity based on the image source URL:
    # /wp-content/plugins/rsl-assets/assets/artwork/affinity/magic.png is Magic
    affinity_map = {
        "force": "Force",
        "magic": "Magic",
        "spirit": "Spirit",
        "void": "Void"
    }

    #affinity_key = os.path.splitext(os.path.basename(affinity_source))[0]
    affinity_key = affinity_source.rsplit("/", 1)[-1].split(".")[0]

    if affinity_key in affinity_map:
        return affinity_map[affinity_key]
    print("Warning: Could not determine affinity from source:", affinity_source)
    return None

def get_ratings_from_list(raiting_list):
    ratings = {}
    for item in raiting_list:
        text = item.get_text(separator=" ", strip=True)
        key, value = text.split(":", 1) if ":" in text else (text, "")

        if is_numeric(value.strip()):
            ratings[key.strip()] = float(value.strip())
        else:
            stars = item.find("div", class_="star-ratings")
            if stars:
                ratings[key.strip()] = count_stars(stars)
            else:
                print(f"Warning: No star ratings found for item: {text.strip()}.")
    return ratings

def count_stars(stars):
    star_count = len(stars.find_all("i", class_="fas fa-star"))
    half_stars = len(stars.find_all("i", class_="fas fa-star-half"))
    if (star_count + half_stars) != len(stars):
        print(f"Warning: Did not count all stars. Expected {len(stars)} but counted {star_count} full stars and {half_stars} half stars.")

    star_rating = star_count + (0.5 * half_stars)
    if star_rating == 0:  
        print(f"Warning: No stars found in expected structure: {stars}")

    return star_rating

def getName(soup):
    # Locate the name:
    name_div = soup.find("div", class_="fusion-title title fusion-title-1 fusion-sep-none fusion-title-text fusion-title-size-one")
    if not name_div:
        print("Warning: Could not find the champion name.")
        return None
    name_header = name_div.find("h1")
    if not name_header:
        print("Warning: Could not find the champion name header.")
        return None
    name = name_header.get_text(strip=True)
    if not name:
        print("Warning: Champion name is empty.")
        return None
    
    return name

def getFactionAffinity(soup):
    # Locate the faction and affinity:
    # Affinity icons: <div class="raid-affinity-icon">
    # <img class="affinity-icon lazyloaded" data-orig-src="/wp-content/plugins/rsl-assets/assets/factions/shadowkin.png" decoding="async" src="/wp-content/plugins/rsl-assets/assets/factions/shadowkin.png"/>
    # <img class="affinity-icon lazyloaded" data-orig-src="/wp-content/plugins/rsl-assets/assets/artwork/affinity/magic.png" decoding="async" src="/wp-content/plugins/rsl-assets/assets/artwork/affinity/magic.png"/
    # </div>

    affinity_icons = soup.find("div", class_="raid-affinity-icon")

    icon_sources = affinity_icons.find_all("img")
    if not icon_sources:
        print("Warning: Could not find any affinity icons.")
        return None, None

    if len(icon_sources) < 2:
        print("Warning: Does not have both faction and affinity sources.")
        return None, None

    # The first icon is the faction icon:
    faction_source = icon_sources[0]["src"]
    if not faction_source:
        print("Warning: Could not find the champion's faction icon.")
        return None, None

    faction = getFactionFromSource(faction_source)
    if not faction:
        print("Warning: Could not determine faction from source:", faction_source)
        return None, None

    # The second icon is the affinity icon:
    affinity_source = icon_sources[1]["src"]
    if not affinity_source:
        print("Warning: Could not find the champion's affinity icon. :", icon_sources[1])
    
    affinity = getAffinityFromSource(affinity_source)
    if not affinity:
        print("Warning: Could not determine affinity from source:", affinity_source)
        return faction, None  # Return faction even if affinity is None

    return faction, affinity

def getOverallRating(soup):
    # Get overall rating:
    # <div class="raid-ratings-overall" id="overall-rating">
    # <div class="raid-rating">
    # <span>4.5</span>
    # <i class="fas fa-star" aria-hidden="true"></i>
    # </div>
    # <h3 data-fontsize="22.4" style="--fontSize: 22.4; line-height: 1.3; --minFontSize: 22.4;" data-lineheight="29.12px" class="fusion-responsive-typography-calculated">Overall Rating</h3>
    # </div>

    overall_rating = soup.find("div", class_="raid-ratings-overall")
    if not overall_rating:
        print("Warning: Could not find overall rating.")
        return None
    raid_raiting = overall_rating.find("div", class_="raid-rating")
    if not raid_raiting:
        print("Warning: Could not find overall raid rating.")
        return None
    overall_rating_value = raid_raiting.get_text(strip=True)
    if not overall_rating_value:
        print("Warning: Overall rating value is empty.")
        return None
    
    if is_numeric(overall_rating_value):
        return float(overall_rating_value)
    else:
        print(f"Warning: Overall rating value is not numeric: {overall_rating_value}")
        return None
    
def getCoreRatings(soup):
    # Get Core Ratings:
    # <div class="raid-ratings-content" id="key-areas">
    # <h3 data-fontsize="22.4" style="--fontSize: 22.4; line-height: 1.3; --minFontSize: 22.4;" data-lineheight="29.12px" class="fusion-responsive-typography-calculated">Core Areas</h3>
    coreRatings = champion.CoreRatings()
    key_area = soup.find("div", id="key-areas")
    if not key_area:
        print("Warning: Could not find key areas content.")
        return None

    # Locate the ratings list inside key-area
    ratings_list = key_area.find("div", class_="raid-ratings-list")
    if not ratings_list:
        print("Warning: Could not find the raid ratings list.")
        return None

    # Find all individual rating items using their class
    rating_items = ratings_list.find_all("div", class_="raid-rating")
    if not rating_items:
        print("Warning: No rating items found.")
        return None
    
    core_ratings = get_ratings_from_list(rating_items)
    for key, value in core_ratings.items():
        if is_numeric(str(value)):
            coreRatings.setRating(key, float(value))
        else:
            print(f"Warning: Core rating for '{key}' is not numeric: {value}")

    return coreRatings

def getDungeonRatings(soup):
    # Get Dungeon Ratings:
    # <div class="raid-ratings-content" id="dungeons">
    # <h3 data-fontsize="22.4" style="--fontSize: 22.4; line-height: 1.3; --minFontSize: 22.4;" data-lineheight="29.12px" class="fusion-responsive-typography-calculated">Dungeons</h3>
    dungeonRatings = champion.DungeonRatings()
    dungeon_areas = soup.find("div", id="dungeons")
    if not dungeon_areas:
        print("Warning: Could not find dungeon areas content.")
        return None
    
    # Locate the ratings list inside dungeon-areas
    dungeon_ratings_list = dungeon_areas.find("div", class_="raid-ratings-list")
    if not dungeon_ratings_list:
        print("Warning: Could not find the dungeon ratings list.")
        return None

    # Find all individual rating items using their class
    dungeon_rating_items = dungeon_ratings_list.find_all("div", class_="raid-rating")
    if not dungeon_rating_items:
        print("Warning: No dungeon rating items found.")
        return None


    dungeon_ratings = get_ratings_from_list(dungeon_rating_items)
    for key, value in dungeon_ratings.items():
        if is_numeric(str(value)):
            dungeonRatings.setRating(key, float(value))
        else:
            print(f"Warning: Dungeon rating for '{key}' is not numeric: {value}")

    return dungeonRatings

def getHardModeRatings(soup):
    # Get Hard Mode Ratings:
    # <div class="raid-ratings-content" id="hard-mode">
    # <h3 data-fontsize="22.4" style="--fontSize: 22.4; line-height: 1.3; --minFontSize: 22.4;" data-lineheight="29.12px" class="fusion-responsive-typography-calculated">Hard Mode</h3>
    hardModeRatings = champion.HardModeRatings()
    hard_mode_areas = soup.find("div", id="hard-mode")
    if not hard_mode_areas:
        print("Warning: Could not find hard mode areas content.")
        return None
    
    # Locate the ratings list inside hard-mode-areas
    hard_mode_ratings_list = hard_mode_areas.find("div", class_="raid-ratings-list")
    if not hard_mode_ratings_list:
        print("Warning: Could not find the hard mode ratings list.")
        return None
    # Find all individual rating items using their class
    hard_mode_rating_items = hard_mode_ratings_list.find_all("div", class_="raid-rating")
    if not hard_mode_rating_items:
        print("Warning: No hard mode rating items found.")
        return None
    
    hard_mode_ratings = get_ratings_from_list(hard_mode_rating_items)
    for key, value in hard_mode_ratings.items():
        if is_numeric(str(value)):
            hardModeRatings.setRating(key, float(value))
        else:
            print(f"Warning: Hard mode rating for '{key}' is not numeric: {value}")

    return hardModeRatings

def getDoomTowerRatings(soup):
    #Get Doom Tower Ratings:
    # <div class="raid-ratings-content raid-ratings-double" id="doom-tower">
    # <h3 data-fontsize="22.4" style="--fontSize: 22.4; line-height: 1.3; --minFontSize: 22.4;" data-lineheight="29.12px" class="fusion-responsive-typography-calculated">Doom Tower</h3>
    doomTowerRatings = champion.DoomTowerRatings()
    doom_tower_areas = soup.find("div", id="doom-tower")
    if not doom_tower_areas:
        print("Warning: Could not find doom tower areas content.")
        return None
    
    # Locate the ratings list inside doom-tower-areas
    doom_tower_ratings_list = doom_tower_areas.find("div", class_="raid-ratings-list")
    if not doom_tower_ratings_list:
        print("Warning: Could not find the doom tower ratings list.")
        return None
    
    # Find all individual rating items using their class
    doom_tower_rating_items = doom_tower_ratings_list.find_all("div", class_="raid-rating")
    if not doom_tower_rating_items:
        print("Warning: No doom tower rating items found.")
        return None
    
    doom_tower_ratings = get_ratings_from_list(doom_tower_rating_items)
    for key, value in doom_tower_ratings.items():
        if is_numeric(str(value)):
            doomTowerRatings.setRating(key, float(value))
        else:
            print(f"Warning: Doom tower rating for '{key}' is not numeric: {value}")
    
    return doomTowerRatings

def getFactionWarsRatings(soup):
    # Get Faction Wars Ratings:
    # <div class="raid-ratings-content" id="faction-wars">
    # <h3 data-fontsize="22.4" style="--fontSize: 22.4; line-height: 1.3; --minFontSize: 22.4;" data-lineheight="29.12px" class="fusion-responsive-typography-calculated">Faction Wars</h3>

    factionWarsRatings = champion.FactionWarsRatings()
    faction_wars_areas = soup.find("div", id="faction-wars")
    if not faction_wars_areas:
        print("Warning: Could not find faction wars areas content.")
        return None
    
    # Locate the ratings list inside faction-wars-areas
    faction_wars_ratings_list = faction_wars_areas.find("div", class_="raid-ratings-list")

    if not faction_wars_ratings_list:
        print("Warning: Could not find the faction wars ratings list.")
        return None
    
    # Find all individual rating items using their class
    # <div class="raid-rating faction-wars">
    #   <div class="raid-rating-label">Damage:</div>
	#   Godlike
    # </div>

    faction_wars_rating_items = faction_wars_ratings_list.find_all("div", class_="raid-rating faction-wars")
    if not faction_wars_rating_items:
        print("Warning: No faction wars rating items found.")
        return None
    
    for item in faction_wars_rating_items:
        text = item.get_text(separator=" ", strip=True)
        if ":" in text:
            key, value = text.split(":", 1)
            key = key.strip()
            value = value.strip()
            factionWarsRatings.setRating(key, value)
        else:
            print(f"Warning: Faction wars rating item does not contain a colon: {text}")

    return factionWarsRatings

def load_hell_Hades(html):
    this_champion = champion.Champion()
    soup = BeautifulSoup(html, "html.parser")
    
    this_champion.name = getName(soup)
    if not this_champion.name:
        print("Warning: Champion name could not be determined.")
        return None

    this_champion.faction, this_champion.affinity = getFactionAffinity(soup)
    if not this_champion.faction or not this_champion.affinity:
        print("Warning: Champion faction or affinity could not be determined.")
        return None
    
    this_champion.ratings.overall = getOverallRating(soup)
    if this_champion.ratings.overall is None:
        print("Warning: Overall rating could not be determined.")
        return None

    this_champion.ratings.core = getCoreRatings(soup)
    if not this_champion.ratings.core:
        print("Warning: Core ratings could not be determined.")
        return None

    this_champion.ratings.dungeons = getDungeonRatings(soup)
    if not this_champion.ratings.dungeons:
        print("Warning: Dungeon ratings could not be determined.")
        return None

    this_champion.ratings.hard_mode = getHardModeRatings(soup)
    if not this_champion.ratings.hard_mode:
        print("Warning: Hard mode ratings could not be determined.")
        return None

    this_champion.ratings.doom_tower = getDoomTowerRatings(soup)
    if not this_champion.ratings.doom_tower:
        print("Warning: Doom tower ratings could not be determined.")
        return None

    # this_champion.ratings.faction_wars = getFactionWarsRatings(soup)
    # if not this_champion.ratings.faction_wars:
    #     print("Warning: Faction wars ratings could not be determined.")
    #     return None

    return this_champion
