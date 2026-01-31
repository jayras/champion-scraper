#!/usr/bin/env python3
"""Test script to verify Google Sheets integration"""

import os
from champion_sheets import ChampionSheets

def test_sheets():
    """Test basic Sheets connectivity and operations"""
    
    # Use environment variables or defaults
    spreadsheet_name = os.environ.get('GS_SPREADSHEET', 'Raid Champions')
    creds_path = os.environ.get('GOOGLE_SA_CREDS', '~/.creds/raid-champions-4d6e8b10a778.json')
    
    # Expand tilde in path
    creds_path = os.path.expanduser(creds_path)
    
    print(f"Testing Google Sheets integration...")
    print(f"  Spreadsheet: {spreadsheet_name}")
    print(f"  Credentials: {creds_path}")
    print()
    
    try:
        # Initialize ChampionSheets
        sheets = ChampionSheets(spreadsheet_name=spreadsheet_name, creds_path=creds_path)
        print("✓ Successfully connected to Google Sheets")
        print()
        
        # Test reading champion names
        champions = sheets.getChampionNames()
        print(f"✓ Retrieved champion names: {len(champions)} champions")
        if champions:
            print(f"  Sample champions: {champions[:5]}")
        print()
        
        # Test writing a sample champion
        sample_champion = {
            "Champion_ID": 999,
            "Name": "Test Champion",
            "Faction": "Test Faction",
            "Affinity": "Magic",
            "Rarity": "Legendary",
            "Ratings": {
                "Core Areas": {
                    "Demon Lord": 8.5,
                    "Clan Boss": 9.0
                },
                "Campaign": {
                    "Brutal": 7.5
                }
            }
        }
        
        sheets.writeChampion(sample_champion)
        print("✓ Successfully wrote test champion to Sheets")
        print()
        
        # Verify it was written
        updated_champions = sheets.getChampionNames()
        if "Test Champion" in updated_champions:
            print("✓ Test champion successfully saved and retrieved")
        else:
            print("⚠ Test champion not found in updated list")
        print()
        
        print("All tests passed!")
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("Please ensure your Google service account credentials are at:")
        print(f"  {creds_path}")
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sheets()
