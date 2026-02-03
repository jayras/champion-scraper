import getPage
import loadChampion
from champion_sheets import ChampionSheets
import champion_reports
import os
import sys
import argparse
import pandas as pd
from champion_database import ChampionDatabase

def scrape_and_load(db, xcel):
        """Scrape champions from Hellhades and persist to DB, then sync to Sheets."""
        print("\n📖 Reading champion list from Google Sheets...")
        names = xcel.getChampionNames()
        print(f"Found {len(names)} champions to process")

        print("\n🔄 Scraping champion data from Hellhades...")
        scraped_count = 0
        failed_count = 0

        for name in names:
            print(f"Loading champion: {name}")
            page = getPage.get_hellhades_page(name)

            if not page:
                print(f"❌ Failed to retrieve page for {name}")
                failed_count += 1
                continue

            champion = loadChampion.load_hell_Hades(page)
            if not champion:
                print(f"❌ Failed to load champion data for {name}")
                failed_count += 1
                continue

            print(f"✓ Champion {champion.name} loaded successfully!")

            # Persist ONLY to DB (DB is source of truth)
            champ_json = champion.toJson(as_dict=True)
            champion_id = db.save_champion(champ_json)
            db.save_ratings(champion_id=champion_id, ratings_data=champ_json.get("Ratings", {}))
            print(f"  Saved to DB with ID {champion_id}")
            
            scraped_count += 1

        print(f"\n✓ Scraping complete: {scraped_count} champions loaded, {failed_count} failed")

        # Now query the database to build the sheets data
        print("\n📊 Querying database to sync with Google Sheets...")
        db_path = db.cursor.connection.execute("PRAGMA database_list").fetchone()[2]
        
        # Get all champions from DB
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT champion_id, name, faction, affinity, rarity
            FROM champions
            ORDER BY champion_id
        """)
        
        champions_data = cursor.fetchall()
        df_champs = pd.DataFrame(champions_data, columns=["Champion_ID", "Name", "Faction", "Affinity", "Rarity"])
        
        # Get all ratings from DB
        cursor.execute("""
            SELECT champion_id, category, subcategory, rating
            FROM ratings
            ORDER BY champion_id, category, subcategory
        """)
        
        ratings_data = cursor.fetchall()
        df_ratings = pd.DataFrame(ratings_data, columns=["Champion_ID", "Category", "Battle", "Rating"])
        
        conn.close()
        
        print(f"  Found {len(df_champs)} champions and {len(df_ratings)} ratings in database")
        
        # Write both sheets once, at the end
        print("\n📤 Writing to Google Sheets (batch operation)...")
        xcel._write_sheet_df(xcel.CHAMPIONS_SHEET, df_champs)
        xcel._write_sheet_df(xcel.RATINGS_SHEET, df_ratings)
        
        print("\n✓ Sync complete!")

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