## Project high-level overview

- Purpose: scrape Raid Shadow Legends champion ratings from Hellhades and persist them to an Excel file and a local SQLite DB.
- Flow: `main.py` -> `ChampionExcel.getChampionNames()` -> `getPage.get_hellhades_page(name)` -> `loadChampion.load_hell_Hades(html)` -> persist via `ChampionExcel.writeChampion()` and `ChampionDatabase.save_champion()`/`save_ratings()`.

## Critical files & roles

- `main.py`: entrypoint and orchestration. See `scrape_and_load(db, xcel)` for the main loop and example `db.pull_data()` call.
- `getPage.py`: uses Selenium + headless Chrome to render pages. Caller expects an HTML string or `None` on failure.
- `loadChampion.py`: parses rendered HTML with BeautifulSoup and returns a `Champion` (from `champion.py`) or `None` if parsing fails.
- `champion.py`: domain model. Objects expose `toJson(as_dict=True)` for downstream persistence.
- `champion_excel.py`: reads/writes Excel sheets (`Champions`, `Ratings`) via `pandas` and `xlsxwriter`.
- `champion_database.py`: local SQLite schema and upsert logic for champions and ratings.

## Environment & runtime notes

- Required Python packages: `selenium`, `beautifulsoup4`, `pandas`, `xlsxwriter` (installed via `pip`).
- System dependency: Chrome/Chromium + matching `chromedriver` on PATH for `getPage.py` to work. `getPage` starts a headless Chrome session.
- Run locally: `python3 main.py` (ensure output/ folder exists or adapt paths in `main.py`).

## Project-specific conventions and patterns

- Data objects: `Champion` and nested rating classes implement `toJson(as_dict=True)` and are passed as dictionaries for persistence. Preserve this contract when changing models.
- Failure signaling: parser and network helpers return `None` on failure and print warnings. Consumers check for falsy values and abort gracefully.
- Excel representation: `ChampionExcel` keeps `Champions` and `Ratings` sheets; new champion entries replace old by `Champion_ID` and ratings are replaced for that champion.
- DB schema: `champions(name UNIQUE)` and `ratings` use `UNIQUE(champion_id, category, subcategory) ON CONFLICT REPLACE`. When updating SQL logic, preserve these upsert semantics.

## Common edit examples for AI agents

- To add a new parsing rule for a rating section, update `loadChampion.py` functions (e.g. `getCoreRatings`) and ensure the new values are stored in the nested `ChampionRatings` structures in `champion.py`.
- When changing output format, maintain `toJson(as_dict=True)` compatibility so `ChampionExcel.writeChampion()` and `ChampionDatabase.save_ratings()` continue to work.
- To disable live scraping for offline testing, stub `getPage.get_hellhades_page()` to return saved HTML fixtures; tests and local runs rely on that single replacement point.

## Known limitations / gotchas

- `getPage.py` requires chromedriver+Chrome; missing driver causes runtime crashes. Prefer stubbing in CI or when running dry-runs.
- Parsers are brittle: many `Warning:` prints exist (in `getName`, `getRarityAndBookValue`, etc.). Changes to HTML structure on hellhades.com will likely break multiple `get*` functions.
- Numeric detection uses `is_numeric()` and star counting in `loadChampion.py` — preserve that logic if you change DOM traversal.

## What to do when you get stuck

- Reproduce by running `python3 main.py` with a single champion name in `ChampionExcel` or by invoking `getPage.get_hellhades_page('Geomancer')` and `loadChampion.load_hell_Hades(html)` interactively.
- Inspect `champion.py` for the canonical shapes of persisted data; prefer changing parser code to match the model rather than altering persistence routines.

If anything above is unclear or you'd like more examples (unit-test harness, fixtures, or CI setup), tell me which area to expand.
