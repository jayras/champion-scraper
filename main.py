import getPage
import loadChampion


def main():
    print("Champion Scraper is running!")
    # Call your scraping and data processing functions here

    page = getPage.get_hellhades_page("Ninja")

    if page:
        champion = loadChampion.load_hell_Hades(page)
    else:
        print("Utter failure")


if __name__ == "__main__":
    main()

