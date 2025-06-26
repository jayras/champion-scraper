import sqlite3

class ChampionDatabase:
    def __init__(self, db_name="champions.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Creates all necessary tables for champion data."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS champions (
                champion_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                faction TEXT,
                affinity TEXT,
                rarity TEXT
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                champion_id INTEGER,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                rating REAL,
                FOREIGN KEY(champion_id) REFERENCES champions(champion_id)
                UNIQUE(champion_id, category, subcategory) ON CONFLICT REPLACE
            )
        """)
        
        self.conn.commit()

    def save_champion(self, champion_data):
        """Stores or updates champion core details."""
        self.cursor.execute("""
            INSERT INTO champions (name, faction, affinity, rarity)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET 
                faction = excluded.faction,
                affinity = excluded.affinity,
                rarity = excluded.rarity
        """, (
            champion_data["Name"],
            champion_data["Faction"],
            champion_data["Affinity"],
            champion_data["Rarity"]
        ))
        self.conn.commit()

        return self.cursor.lastrowid  # Fetch assigned champion_id

    def save_ratings(self, champion_id, ratings_data):
        """Stores or updates champion ratings dynamically."""
        for category, subcategories in ratings_data.items():
            if isinstance(subcategories, dict):  # Nested categories
                for subcategory, rating in subcategories.items():
                    self.cursor.execute("""
                        INSERT INTO ratings (champion_id, category, subcategory, rating)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(champion_id, category, subcategory) DO UPDATE SET 
                            rating = excluded.rating
                    """, (champion_id, category, subcategory, rating))
            else:  # Direct category ratings (Overall Rating, Book Value)
                self.cursor.execute("""
                    INSERT INTO ratings (champion_id, category, subcategory, rating)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(champion_id, category, subcategory) DO UPDATE SET 
                        rating = excluded.rating
                """, (champion_id, "Overall", category, subcategories))

        self.conn.commit()

    def pull_data(self, category, subcategory, limit = 10):
        self.cursor.execute("""
            SELECT champions.name, ratings.subcategory, ratings.rating 
            FROM champions 
            JOIN ratings ON champions.champion_id = ratings.champion_id
            WHERE ratings.category = ? AND ratings.subcategory = ?
            ORDER BY ratings.rating DESC
            LIMIT ?;
        """, (category, subcategory, limit))

        for row in self.cursor.fetchall():
            print(row)  # Displays top Demon Lord champions

    def close(self):
        """Closes the database connection."""
        self.conn.close()

