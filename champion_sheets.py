import os
import gspread
import pandas as pd
from datetime import datetime
import json

class ChampionSheets:
    """Simple Google Sheets backend compatible with the existing Excel usage.

    Requires a Google service account JSON file and the `gspread` package.
    It provides `getChampionNames()` and `writeChampion(champion_dict)`.
    """

    CHAMPIONS_SHEET = "Champions"
    RATINGS_SHEET = "Ratings"

    def __init__(self, spreadsheet_name=None, creds_path=None):
        spreadsheet_name = spreadsheet_name or os.environ.get('GS_SPREADSHEET', 'Raid Champions')
        creds_path = creds_path or os.environ.get('GOOGLE_SA_CREDS', 'google_service_account.json')
        creds_path = os.path.expanduser(creds_path)

        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Service account credentials not found: {creds_path}")

        self.client = gspread.service_account(filename=creds_path)

        try:
            self.ss = self.client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            self.ss = self.client.create(spreadsheet_name)

        # Create backup directory
        self.backup_dir = os.path.join(os.getcwd(), "output", "sheet_backups")
        os.makedirs(self.backup_dir, exist_ok=True)

        # Ensure worksheets exist and have headers
        self._ensure_sheet(self.CHAMPIONS_SHEET, ["Champion_ID", "Name", "Faction", "Affinity", "Rarity"])
        self._ensure_sheet(self.RATINGS_SHEET, ["Champion_ID", "Category", "Battle", "Rating"])

    def _ensure_sheet(self, title, headers):
        try:
            ws = self.ss.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            ws = self.ss.add_worksheet(title=title, rows=1000, cols=max(10, len(headers)))
            ws.append_row(headers)

    def _read_sheet_df(self, title):
        ws = self.ss.worksheet(title)
        try:
            records = ws.get_all_records()
        except gspread.exceptions.GSpreadException as e:
            # Handle duplicate header issue by getting raw values and building dataframe manually
            if "duplicates" in str(e):
                rows = ws.get_all_values()
                if not rows:
                    return pd.DataFrame()
                # Use first row as headers, clean empty column names
                headers = [h if h else f"Col_{i}" for i, h in enumerate(rows[0])]
                # Remove duplicate column names by appending index
                seen = {}
                clean_headers = []
                for h in headers:
                    if h in seen:
                        seen[h] += 1
                        clean_headers.append(f"{h}_{seen[h]}")
                    else:
                        seen[h] = 0
                        clean_headers.append(h)
                
                data = rows[1:] if len(rows) > 1 else []
                df = pd.DataFrame(data, columns=clean_headers)
                return df
            else:
                raise
        
        if not records:
            return pd.DataFrame(columns=ws.row_values(1))
        return pd.DataFrame.from_records(records)

    def _backup_sheet_df(self, title, df):
        """Save a backup copy of the dataframe to a local file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"{title}_backup_{timestamp}.csv")
        df.to_csv(backup_path, index=False)
        print(f"📦 Backup created: {backup_path}")
        return backup_path

    def restore_from_backup(self, sheet_title, backup_path):
        """Restore a sheet from a backup CSV file"""
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        df = pd.read_csv(backup_path)
        print(f"🔄 Restoring {sheet_title} from {backup_path}")
        self._write_sheet_df_safe(sheet_title, df)
        return True

    def _write_sheet_df_safe(self, title, df):
        """Safely write dataframe to sheet, with data loss protection and backup"""
        ws = self.ss.worksheet(title)
        
        # Get existing data for comparison (with error handling for duplicate headers)
        try:
            existing = ws.get_all_records()
            existing_count = len(existing)
        except gspread.exceptions.GSpreadException:
            # If we can't get records due to duplicate headers, get raw values instead
            rows = ws.get_all_values()
            existing_count = len(rows) - 1 if rows else 0
        
        new_count = len(df)
        
        # Create a backup BEFORE any write operation
        if existing_count > 0:
            try:
                existing_df = pd.DataFrame.from_records(ws.get_all_records())
            except gspread.exceptions.GSpreadException:
                # Build from raw values if records fails
                rows = ws.get_all_values()
                if rows:
                    headers = [h if h else f"Col_{i}" for i, h in enumerate(rows[0])]
                    existing_df = pd.DataFrame(rows[1:], columns=headers)
                else:
                    existing_df = pd.DataFrame()
            
            if not existing_df.empty:
                backup_path = self._backup_sheet_df(title, existing_df)
        
        # Safeguard: don't proceed if we're losing MORE than 1 champion (>2 rows including header)
        if title == "Champions" and existing_count > 1 and new_count < existing_count - 1:
            print(f"❌ WARNING: {title} would lose significant data ({existing_count} → {new_count} rows). Aborting write.")
            if 'backup_path' in locals():
                print(f"✓ Backup saved at: {backup_path}")
            return False
        
        # For other sheets (Ratings), use original threshold
        if title != "Champions" and existing_count > 0 and new_count < existing_count * 0.5:
            print(f"❌ WARNING: {title} would lose significant data ({existing_count} → {new_count} rows). Aborting write.")
            if 'backup_path' in locals():
                print(f"✓ Backup saved at: {backup_path}")
            return False
        
        # Clear and rewrite
        ws.clear()
        if df.empty:
            ws.append_row(list(df.columns))
            return True
        
        # Convert df to list of lists, handling NaN values
        rows = [list(df.columns)]
        for _, row in df.iterrows():
            rows.append([str(val) if val is not None and str(val) != 'nan' else '' for val in row])
        ws.update(rows)
        print(f"✓ {title} updated successfully ({new_count} rows)")
        return True

    def _write_sheet_df(self, title, df):
        """Legacy method - calls safe version"""
        return self._write_sheet_df_safe(title, df)

    def getChampionNames(self):
        df = self._read_sheet_df(self.CHAMPIONS_SHEET)
        if df.empty:
            return []
        return list(df["Name"].dropna().astype(str).values)

    def writeChampion(self, champion_data, champion_id=None):
        """Write champion to Sheets. If champion_id is provided, use it; otherwise assign one."""
        df_champs = self._read_sheet_df(self.CHAMPIONS_SHEET)

        name = champion_data.get("Name")
        
        # If champion_id is provided from DB, use it
        if champion_id:
            final_champion_id = champion_id
        else:
            # Otherwise determine one (for manual entries without DB ID yet)
            if df_champs.empty or "Champion_ID" not in df_champs.columns:
                final_champion_id = 0  # Blank/unassigned
            else:
                # Clean and convert Champion_ID to int
                df_champs["Champion_ID"] = pd.to_numeric(df_champs["Champion_ID"], errors='coerce')
                
                # find existing by name (case-insensitive)
                matches = df_champs[df_champs["Name"].str.lower() == str(name).lower()]
                if not matches.empty:
                    # Use existing champion_id if available, otherwise 0 (unassigned)
                    existing_id = matches.iloc[0]["Champion_ID"]
                    final_champion_id = int(existing_id) if pd.notna(existing_id) and existing_id != 0 else 0
                else:
                    final_champion_id = 0  # New entry, no ID yet

        # Upsert champion row - remove by name (not ID, to preserve manually-added entries)
        if not df_champs.empty:
            df_champs = df_champs[df_champs["Name"].str.lower() != str(name).lower()]
        
        # Create new row with the champion_id (may be 0 if unassigned)
        new_row = {"Champion_ID": final_champion_id,
                   "Name": champion_data.get("Name", ""),
                   "Faction": champion_data.get("Faction", ""),
                   "Affinity": champion_data.get("Affinity", ""),
                   "Rarity": champion_data.get("Rarity", "")}
        
        df_champs = pd.concat([df_champs, pd.DataFrame([new_row])], ignore_index=True)
        # Ensure Champion_ID column is int-like (safe conversion)
        df_champs["Champion_ID"] = pd.to_numeric(df_champs["Champion_ID"], errors='coerce').fillna(0).astype(int)

        self._write_sheet_df(self.CHAMPIONS_SHEET, df_champs)

        # Process ratings
        ratings = champion_data.get("Ratings", {})
        ratings_list = []
        for category, battles in ratings.items():
            if isinstance(battles, dict):
                for battle, rating in battles.items():
                    ratings_list.append({"Champion_ID": champion_id, "Category": category, "Battle": battle, "Rating": rating})
            else:
                ratings_list.append({"Champion_ID": champion_id, "Category": "Overall", "Battle": category, "Rating": battles})

        df_ratings = self._read_sheet_df(self.RATINGS_SHEET)
        if df_ratings.empty:
            df_ratings = pd.DataFrame(columns=["Champion_ID", "Category", "Battle", "Rating"])        

        # Remove old ratings for this champion
        df_ratings = df_ratings[df_ratings["Champion_ID"] != champion_id]
        if ratings_list:
            df_ratings = pd.concat([df_ratings, pd.DataFrame(ratings_list)], ignore_index=True)

        self._write_sheet_df(self.RATINGS_SHEET, df_ratings)
    def writeReport(self, report_name, df_report):
        """Write a report dataframe to a new or existing sheet."""
        # Create or get the report sheet
        try:
            ws = self.ss.worksheet(report_name)
        except gspread.exceptions.WorksheetNotFound:
            ws = self.ss.add_worksheet(title=report_name, rows=len(df_report) + 100, cols=len(df_report.columns) + 5)
        
        self._write_sheet_df(report_name, df_report)