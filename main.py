import getPage
import loadChampion


def main():
    print("Champion Scraper is running!")
    # Call your scraping and data processing functions here
    names = ["Ninja", "Doompriest", "Roshcard the Tower", "Saito", "Tayrel", "Tyrant Ixlimor", "Gurptuk Moss-Beard"]

    for name in names:
        print(f"Loading champion: {name}")
        page = getPage.get_hellhades_page(name)

        if page:
            champion = loadChampion.load_hell_Hades(page)
            if champion:
                print(f"Champion {champion.name} loaded successfully!")
                print(f"Ratings: {champion.ratings}")
            else:
                print(f"Failed to load champion data for {name}")
        else:
            print(f"Failed to retrieve page for {name}")


if __name__ == "__main__":
    main()

