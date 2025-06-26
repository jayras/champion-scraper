import getPage
import loadChampion
from champion_excel import ChampionExcel
import os
from champion_database import ChampionDatabase

def scrape_and_load(db, xcel):
        #Debug:
        names = ["Geomancer"]

        names = xcel.getChampionNames()

        for name in names:
            print(f"Loading champion: {name}")
            page = getPage.get_hellhades_page(name)

            if page:
                champion = loadChampion.load_hell_Hades(page)
                if champion:
                    print(f"Champion {champion.name} loaded successfully!")
                    xcel.writeChampion(champion.toJson(as_dict=True))
                    champion_id = db.save_champion(champion.toJson(as_dict=True))
                    db.save_ratings(champion_id= champion_id, ratings_data=champion.toJson(as_dict=True)["Ratings"])
                    print(f"Champion {champion.name} saved!")
                else:
                    print(f"Failed to load champion data for {name}")
            else:
                print(f"Failed to retrieve page for {name}")

def main():
    db_path = os.path.join(os.getcwd(), "output", "champions.db")  # Saves inside a "data" folder
    excel_path = "output/raid_champions.xlsx"

    print("Champion Scraper is running!")
    db = ChampionDatabase(db_name=db_path)
    xcel = ChampionExcel(file_path=excel_path)

    try:
        scrape_and_load(db, xcel)
        db.pull_data('Core Areas', 'Demon Lord')  # Example of pulling data for Demon Lord champions
    except Exception as e: 
        print(f"An error occurred: {e}")
    finally:
        db.conn.close()
        print("Database connection closed.")
        print("Champion Scraper finished running!")

if __name__ == "__main__":
    main()

