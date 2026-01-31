import os
import gspread
import pandas as pd

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

        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Service account credentials not found: {creds_path}")

        self.client = gspread.service_account(filename=creds_path)

        try:
            self.ss = self.client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            self.ss = self.client.create(spreadsheet_name)

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
        records = ws.get_all_records()
        if not records:
            return pd.DataFrame(columns=ws.row_values(1))
        return pd.DataFrame.from_records(records)

    def _write_sheet_df(self, title, df):
        ws = self.ss.worksheet(title)
        # Clear and rewrite
        ws.clear()
        if df.empty:
            ws.append_row(list(df.columns))
            return
        rows = [list(df.columns)] + df.fillna("").values.tolist()
        ws.update(rows)

    def getChampionNames(self):
        df = self._read_sheet_df(self.CHAMPIONS_SHEET)
        if df.empty:
            return []
        return list(df["Name"].dropna().astype(str).values)

    def writeChampion(self, champion_data):
        # champion_data is expected to be a dict produced by Champion.toJson(as_dict=True)
        df_champs = self._read_sheet_df(self.CHAMPIONS_SHEET)

        name = champion_data.get("Name")
        if df_champs.empty:
            champion_id = 1
            df_champs = pd.DataFrame(columns=["Champion_ID", "Name", "Faction", "Affinity", "Rarity"])
        else:
            # find existing
            matches = df_champs[df_champs["Name"].str.lower() == str(name).lower()]
            if not matches.empty:
                champion_id = int(matches.iloc[0]["Champion_ID"])
            else:
                champion_id = int(df_champs["Champion_ID"].max()) + 1

        # Upsert champion row
        new_row = {"Champion_ID": champion_id,
                   "Name": champion_data.get("Name", ""),
                   "Faction": champion_data.get("Faction", ""),
                   "Affinity": champion_data.get("Affinity", ""),
                   "Rarity": champion_data.get("Rarity", "")}

        df_champs = df_champs[df_champs["Champion_ID"] != champion_id]
        df_champs = pd.concat([df_champs, pd.DataFrame([new_row])], ignore_index=True)
        # Ensure Champion_ID column is int-like
        df_champs["Champion_ID"] = df_champs["Champion_ID"].astype(int)

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
