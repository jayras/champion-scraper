import getPage
import loadChampion
from champion_sheets import ChampionSheets
import champion_reports
import os
import sys
import argparse
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
                    # Save to database first to get the champion_id
                    champion_id = db.save_champion(champion.toJson(as_dict=True))
                    # Save ratings with the DB-assigned champion_id
                    db.save_ratings(champion_id=champion_id, ratings_data=champion.toJson(as_dict=True)["Ratings"])
                    # Now write to Sheets with the DB-assigned champion_id
                    xcel.writeChampion(champion.toJson(as_dict=True), champion_id=champion_id)
                    print(f"Champion {champion.name} saved!")
                else:
                    print(f"Failed to load champion data for {name}")
            else:
                print(f"Failed to retrieve page for {name}")

def generate_champion_report(db, xcel):
    """Generate a comprehensive champion report and write to Sheets."""
    print("\n📊 Generating Champion Report...")
    
    db_path = db.cursor.connection.execute("PRAGMA database_list").fetchone()[2]
    
    # Generate the report
    df_report = champion_reports.get_champion_report(db_path, include_ratings=True)
    
    if df_report.empty:
        print("⚠️  No champions found in database.")
        return
    
    # Write to Sheets
    xcel.writeReport("Champion Report", df_report)
    print(f"✓ Champion Report created with {len(df_report)} champions")


def generate_comparison_report(db, xcel, category, subcategory, limit=20):
    """Generate a comparison report for a specific category."""
    print(f"\n📊 Generating Comparison Report: {category} - {subcategory}...")
    
    db_path = db.cursor.connection.execute("PRAGMA database_list").fetchone()[2]
    
    # Generate the report
    df_report = champion_reports.get_champion_comparison_report(db_path, category, subcategory, limit)
    
    if df_report.empty:
        print(f"⚠️  No data found for {category} - {subcategory}.")
        return
    
    # Write to Sheets
    report_name = f"{category} - {subcategory}"
    xcel.writeReport(report_name, df_report)
    print(f"✓ {report_name} Report created with {len(df_report)} champions")


def generate_missing_data_report(db, xcel):
    """Generate a report of champions with missing data."""
    print("\n📊 Generating Missing Data Report...")
    
    db_path = db.cursor.connection.execute("PRAGMA database_list").fetchone()[2]
    
    # Generate the report
    df_report = champion_reports.get_missing_data_report(db_path)
    
    if df_report.empty:
        print("✓ All champions have complete data!")
        return
    
    # Write to Sheets
    xcel.writeReport("Missing Data Report", df_report)
    print(f"⚠️  Missing Data Report created - {len(df_report)} champions with incomplete data")


def generate_single_champion_report(db, xcel, champion_name):
    """Generate a detailed report for a single champion."""
    print(f"\n📊 Generating Champion Report for: {champion_name}...")
    
    db_path = db.cursor.connection.execute("PRAGMA database_list").fetchone()[2]
    
    # Generate the report
    df_report = champion_reports.get_single_champion_report(db_path, champion_name)
    
    if df_report.empty:
        print(f"❌ Champion '{champion_name}' not found in database.")
        return
    
    # Get the champion name from the report for the sheet name
    champ_name = df_report[df_report["Field"] == "Name"]["Value"].values[0] if "Name" in df_report["Field"].values else champion_name
    
    # Write to Sheets with a clean sheet name
    report_sheet_name = f"Champion - {champ_name}"
    xcel.writeReport(report_sheet_name, df_report)
    print(f"✓ Champion Report created: {report_sheet_name}")

def main():
    db_path = os.path.join(os.getcwd(), "output", "champions.db")
    spreadsheet_name = os.environ.get('GS_SPREADSHEET', 'Raid Champions')
    creds_path = os.environ.get('GOOGLE_SA_CREDS', '~/.creds/raid-champions-4d6e8b10a778.json')

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Champion Scraper - Scrape and manage Raid Shadow Legends champion data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scrape                           - Scrape new champion data from Hellhades
  %(prog)s report                           - Generate comprehensive champion report
  %(prog)s champion --name "Geomancer"      - Generate report for specific champion
  %(prog)s compare --category "Core Areas" --subcategory "Demon Lord" --limit 15
  %(prog)s missing                          - Find champions with incomplete data
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape new champion data from Hellhades')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate comprehensive champion report')

    # Champion command
    champion_parser = subparsers.add_parser('champion', help='Generate report for a specific champion')
    champion_parser.add_argument('--name', required=True, help='Champion name')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Generate comparison report for a category')
    compare_parser.add_argument('--category', required=True, help='Rating category (e.g., "Core Areas")')
    compare_parser.add_argument('--subcategory', required=True, help='Rating subcategory (e.g., "Demon Lord")')
    compare_parser.add_argument('--limit', type=int, default=20, help='Number of champions to show (default: 20)')

    # Missing command
    missing_parser = subparsers.add_parser('missing', help='Find champions with incomplete data')

    args = parser.parse_args()

    print("Champion Scraper is running!")
    db = ChampionDatabase(db_name=db_path)
    xcel = ChampionSheets(spreadsheet_name=spreadsheet_name, creds_path=creds_path)

    try:
        if args.command == 'scrape':
            print("Scraping mode: Loading new champion data")
            scrape_and_load(db, xcel)
            db.pull_data('Core Areas', 'Demon Lord')

        elif args.command == 'report':
            print("Report mode: Generating comprehensive champion report")
            generate_champion_report(db, xcel)

        elif args.command == 'champion':
            print(f"Champion mode: Generating report for {args.name}")
            generate_single_champion_report(db, xcel, args.name)

        elif args.command == 'compare':
            print(f"Comparison mode: {args.category} - {args.subcategory}")
            generate_comparison_report(db, xcel, args.category, args.subcategory, args.limit)

        elif args.command == 'missing':
            print("Missing data mode: Checking for incomplete data")
            generate_missing_data_report(db, xcel)

        else:
            # Default: show help
            parser.print_help()

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.conn.close()
        print("Database connection closed.")
        print("Champion Scraper finished running!")


if __name__ == "__main__":
    main()