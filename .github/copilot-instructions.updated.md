## Copilot instructions — champion-scraper (concise)

- Purpose: scrape champion ratings from Hellhades and persist to Google Sheets and a local SQLite DB.

- Core flow: `main.py` -> `ChampionSheets.getChampionNames()` -> `getPage.get_hellhades_page(name)` -> `loadChampion.load_hell_Hades(html)` -> persist via `ChampionSheets.writeChampion()` and `ChampionDatabase.save_*()`.

Key files
- `main.py`: orchestrator and entrypoint. Run `python3 main.py`. Ensure `output/` exists (or adapt paths in `main.py`).
- `getPage.py`: launches headless Chrome via Selenium and returns an HTML string or `None`. Requires Chrome/Chromium + matching `chromedriver` on PATH.
- `loadChampion.py`: BeautifulSoup parsers that return a `Champion` object or `None` on failure.
- `champion.py`: domain model. Persist via `Champion.toJson(as_dict=True)` (contract must be preserved).
- `champion_sheets.py`: Google Sheets backend (replaces Excel). Provides `getChampionNames()` and `writeChampion()`.
- `champion_database.py`: SQLite upserts; keep `champions(name UNIQUE)` and `ratings UNIQUE(champion_id, category, subcategory) ON CONFLICT REPLACE` semantics.

Conventions & patterns (repo-specific)
- Failure signaling: helpers return `None` and print warnings — callers defensively check falsy values.
- Data shape: code passes dictionaries produced by `toJson(as_dict=True)` into Excel/DB layers; do not change that shape silently.
- Sheets behavior: `Champions` and `Ratings` worksheets mirror the old Excel layout. `Champion_ID` is assigned/upserted and ratings rows for a champion are replaced on `writeChampion()`.
- Parsers are brittle: `loadChampion.py` uses `is_numeric()` and star-count heuristics — prefer minimal, well-tested parser edits.

Dev/debug tips
- Quick interactive check (one-liner):
```
python3 -c "from getPage import get_hellhades_page; from loadChampion import load_hell_Hades; html=get_hellhades_page('Geomancer'); print(load_hell_Hades(html))"
```
- Validate Selenium setup: run `python3 testSelenium.py`.
- Offline testing: stub `getPage.get_hellhades_page()` to return saved HTML fixtures and exercise `loadChampion.load_hell_Hades(html)`.

Environment & Google Sheets setup
- Python deps: `selenium`, `beautifulsoup4`, `pandas`, plus `gspread` and `google-auth` for Sheets (install with `pip install gspread google-auth`).
- System deps: Chrome/Chromium + chromedriver that matches your Chrome install.
- Google service account: create a service account in Google Cloud, enable the Google Sheets API and Drive API, create a JSON key, and save it in the repo or on the runner (recommended path: `google_service_account.json`).
- Share or allow the service account to access the target spreadsheet: note the service account email (in the JSON) and share the spreadsheet with that email, or let the library create the sheet under the service account.

Env vars supported by `main.py`:
- `GS_SPREADSHEET` — spreadsheet name (default: `Raid Champions`).
- `GOOGLE_SA_CREDS` — path to the service account JSON (default: `google_service_account.json`).

When changing parser or persistence
- Preserve `Champion.toJson(as_dict=True)` and the DB upsert semantics.
- Add parsing rules in `loadChampion.py` and map into `ChampionRatings` structures in `champion.py`.

Quick verification (example)
```
# install deps
pip install gspread google-auth

# run a quick interactive check (uses creds at GOOGLE_SA_CREDS or google_service_account.json)
python3 -c "from champion_sheets import ChampionSheets; s=ChampionSheets(); print(s.getChampionNames())"
```

If any part is unclear or you want CI/test fixtures added, tell me which area to expand.
