import pandas as pd
import os

# Define file path
file_path = "output/raid_champions.xlsx"

def championToExcel(champion_data):
    """Updates or appends a champion's ratings to an Excel file."""
    
    # Load existing data if file exists
    if os.path.exists(file_path):
        with pd.ExcelFile(file_path) as existing:
            df_champions = pd.read_excel(existing, sheet_name="Champions")
            df_ratings = pd.read_excel(existing, sheet_name="Ratings")
    else:
        df_champions = pd.DataFrame(columns=["Champion_ID", "Name", "Faction", "Affinity", "Rarity"])
        df_ratings = pd.DataFrame(columns=["Champion_ID", "Category", "Battle", "Rating"])

    # **Check if the champion already exists**
    existing_entry = df_champions[df_champions["Name"].str.lower() == champion_data["Name"].lower()]

    if not existing_entry.empty:
        champion_id = existing_entry.iloc[0]["Champion_ID"]  # Use existing ID
    else:
        champion_id = df_champions["Champion_ID"].max() + 1 if not df_champions.empty else 1

    # Append new champion data
    new_champion = pd.DataFrame([{
        "Champion_ID": champion_id,
        "Name": champion_data["Name"],
        "Faction": champion_data["Faction"],
        "Affinity": champion_data["Affinity"],
        "Rarity": champion_data["Rarity"]
    }])
    df_champions = df_champions[df_champions["Champion_ID"] != champion_id]  # Remove old entry if exists
    df_champions = pd.concat([df_champions, new_champion], ignore_index=True)

    # **Process Ratings**
    ratings_list = []
    for category, battles in champion_data["Ratings"].items():
        if isinstance(battles, dict):
            for battle, rating in battles.items():
                ratings_list.append({"Champion_ID": champion_id, "Category": category, "Battle": battle, "Rating": rating})
        else:
            ratings_list.append({"Champion_ID": champion_id, "Category": "Overall", "Battle": category, "Rating": battles})

    new_ratings = pd.DataFrame(ratings_list)

    # **Remove old ratings for this champion before appending fresh**
    df_ratings = df_ratings[df_ratings["Champion_ID"] != champion_id]
    df_ratings = pd.concat([df_ratings, new_ratings], ignore_index=True)

    # **Save back to Excel**
    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        df_champions.to_excel(writer, sheet_name="Champions", index=False)
        df_ratings.to_excel(writer, sheet_name="Ratings", index=False)

def getChampionNames(file_path):
    # Load champions
    if os.path.exists(file_path):
        with pd.ExcelFile(file_path) as existing:
            df_champions = pd.read_excel(existing, sheet_name="Champions")
            df_ratings = pd.read_excel(existing, sheet_name="Ratings")
            champion_names = df_champions.set_index("Champion_ID")["Name"].to_dict()

            return list(champion_names.values())
    else:
        print(f"File {file_path} does not exist.")
        return []
