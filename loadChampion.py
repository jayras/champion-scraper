from bs4 import BeautifulSoup
import os
import champion
from champion import Champion
import re

def is_numeric(s):
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", s))

def getFactionFromSource(faction_source):
    # Gets faction based on the image source URL:
    # /wp-content/plugins/rsl-assets/assets/factions/shadowkin.png is Shadowkin
    #Warning: Could not determine affinity from source: /wp-content/plugins/rsl-assets/assets/factions/shadowkin.png
    faction_map = {
        "shadowkin": "Shadowkin",
        "high_elves": "High Elves",
        "barbarians": "Barbarians",
        "orcs": "Orcs",
        "dwarves": "Dwarves",
        "lizardmen": "Lizardmen",
        "undead_hordes": "Undead Hordes",
        "knight_revenant": "Knight Revenant",
        "dark_elves": "Dark Elves",
        "skinwalkers": "Skinwalkers",
        "ogre": "Ogre",
        "demons": "Demons",
        "void": "Void"
    }

    faction_key = os.path.splitext(os.path.basename(faction_source))[0]

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

    affinity_key = os.path.splitext(os.path.basename(affinity_source))[0]

    if affinity_key in affinity_map:
        return affinity_map[affinity_key]
    print("Warning: Could not determine affinity from source:", affinity_source)
    return None


def load_hell_Hades(html):
    soup = BeautifulSoup(html, "html.parser")

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
    
    # Locate the faction and affinity:
    affinity_icons = soup.find("div", class_="raid-affinity-icon")
    # Affinity icons: <div class="raid-affinity-icon">
    # <img class="affinity-icon lazyloaded" data-orig-src="/wp-content/plugins/rsl-assets/assets/factions/shadowkin.png" decoding="async" src="/wp-content/plugins/rsl-assets/assets/factions/shadowkin.png"/>
    # <img class="affinity-icon lazyloaded" data-orig-src="/wp-content/plugins/rsl-assets/assets/artwork/affinity/magic.png" decoding="async" src="/wp-content/plugins/rsl-assets/assets/artwork/affinity/magic.png"/
    # </div>

    icon_sources = affinity_icons.find_all("img")

    if not icon_sources:
        print("Warning: Could not find any affinity icons.")
        return None

    if len(icon_sources) < 2:
        print("Warning: Does not have both faction and affinity sources.")
        return None

    # The first icon is the faction icon:
    faction_source = icon_sources[0]["src"]

    if not faction_source:
        print("Warning: Could not find the champion's faction icon.")
        return None

    # The second icon is the affinity icon:
    affinity_source = icon_sources[1]["src"]
    if not affinity_source:
        print("Warning: Could not find the champion's affinity icon. :", icon_sources[1])
    
    faction = getFactionFromSource(faction_source)
    affinity = getAffinityFromSource(affinity_source)

    champ_data = Champion(name = name, faction = faction, affinity = affinity)

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

    # Get Core Ratings:
    # <div class="raid-ratings-content" id="key-areas">
    # <h3 data-fontsize="22.4" style="--fontSize: 22.4; line-height: 1.3; --minFontSize: 22.4;" data-lineheight="29.12px" class="fusion-responsive-typography-calculated">Core Areas</h3>

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
    
    coreRatings = champion.coreRatings()
    for idx, item in enumerate(rating_items):
        text = item.get_text(separator=" ", strip=True)
        star_rating = 0.0

        if ":" in text:
            key, value = text.split(":", 1)
            if is_numeric(value.strip()):
                coreRatings.setRating(key.strip(), float(value.strip()))
            else:
                stars = item.find("div", class_="star-ratings")
                if stars:
                    star_rating = count_stars(stars)
                    coreRatings.setRating(key.strip(), star_rating)
                else:
                    print(f"Warning: No star ratings found for item {idx}.")
        else:
            print(f"Warning: Rating item {idx} does not contain a colon to split key and value: {text.strip()}")

    # Debug:
    print(f"Core Ratings: {coreRatings.toJson()}")

    # Get Dungeon Ratings:
    # <div class="raid-ratings-content" id="dungeons">
    # <h3 data-fontsize="22.4" style="--fontSize: 22.4; line-height: 1.3; --minFontSize: 22.4;" data-lineheight="29.12px" class="fusion-responsive-typography-calculated">Dungeons</h3>

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

    dungeonRatings = champion.dungeonRatings()
    dungeon_ratings = get_ratings_from_list(dungeon_rating_items)
    for key, value in dungeon_ratings.items():
        if is_numeric(str(value)):
            dungeonRatings.setRating(key, float(value))
        else:
            print(f"Warning: Dungeon rating for '{key}' is not numeric: {value}")


    # Debug:
    print(f"Dungeon Ratings: {dungeonRatings.toJson()}")

    # Get Hard Mode Ratings:
    # <div class="raid-ratings-content" id="hard-mode">
    # <h3 data-fontsize="22.4" style="--fontSize: 22.4; line-height: 1.3; --minFontSize: 22.4;" data-lineheight="29.12px" class="fusion-responsive-typography-calculated">Hard Mode</h3>
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
    hardModeRatings = champion.hardModeRatings()
    hard_mode_ratings = get_ratings_from_list(hard_mode_rating_items)
    for key, value in hard_mode_ratings.items():
        if is_numeric(str(value)):
            hardModeRatings.setRating(key, float(value))
        else:
            print(f"Warning: Hard mode rating for '{key}' is not numeric: {value}")

    # Debug:
    print(f"Hard Mode Ratings: {hardModeRatings.toJson()}")

    return champ_data

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
    return star_rating
