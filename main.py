import getPage
import loadChampion
import toExcel


def main():
    print("Champion Scraper is running!")
    # Call your scraping and data processing functions here
    # names = ["Ninja", "Doompriest", "Roshcard the Tower", "Saito", "Tayrel", "Tyrant Ixlimor", "Gurptuk Moss-Beard"]
    names = ["Geomancer"]

    # names = [
    #     "Criodan the Blue",
    #     "Pann the Bowhorn",
    #     "Yaga the Insatiable",
    #     "Teryx the Restless",
    #     "Denid the Tusk Knight",
    #     "Branch-arm Lasair",
    #     "Boltsmith"
    # ]


    file_path = "output/raid_champions.xlsx"
    #names = toExcel.getChampionNames(file_path)

    for name in names:
        print(f"Loading champion: {name}")
        page = getPage.get_hellhades_page(name)

        if page:
            champion = loadChampion.load_hell_Hades(page)
            if champion:
                print(f"Champion {champion.name} loaded successfully!\n{champion.toJson(as_dict=False)}")
                toExcel.championToExcel(champion.toJson(as_dict=True))
            else:
                print(f"Failed to load champion data for {name}")
        else:
            print(f"Failed to retrieve page for {name}")


if __name__ == "__main__":
    main()

