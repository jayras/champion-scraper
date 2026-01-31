"""Champion reporting module - generates reports from database data."""

import sqlite3
import pandas as pd
from datetime import datetime


def get_champion_report(db_path, include_ratings=True):
    """
    Generate a comprehensive champion report from the database.
    
    Args:
        db_path: Path to the SQLite database
        include_ratings: Whether to include rating details
    
    Returns:
        DataFrame with champion data and ratings
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query all champions with their basic info
    cursor.execute("""
        SELECT champion_id, name, faction, affinity, rarity
        FROM champions
        ORDER BY champion_id
    """)
    
    champions = cursor.fetchall()
    
    if not champions:
        return pd.DataFrame()
    
    report_data = []
    
    for champ_id, name, faction, affinity, rarity in champions:
        row = {
            "Champion_ID": champ_id,
            "Name": name,
            "Faction": faction or "",
            "Affinity": affinity or "",
            "Rarity": rarity or ""
        }
        
        if include_ratings:
            # Get all ratings for this champion grouped by category
            cursor.execute("""
                SELECT category, subcategory, rating
                FROM ratings
                WHERE champion_id = ?
                ORDER BY category, subcategory
            """, (champ_id,))
            
            ratings = cursor.fetchall()
            
            # Organize ratings into columns (Category - Subcategory: Rating)
            for category, subcategory, rating in ratings:
                col_name = f"{category} - {subcategory}"
                row[col_name] = rating
        
        report_data.append(row)
    
    conn.close()
    
    # Convert to DataFrame, filling missing rating columns with empty strings
    df = pd.DataFrame(report_data)
    df = df.fillna("")
    
    return df


def get_single_champion_report(db_path, champion_name):
    """
    Generate a detailed, readable report for a single champion.
    
    Args:
        db_path: Path to the SQLite database
        champion_name: Name of the champion to report on
    
    Returns:
        DataFrame with champion details formatted for readability
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query the champion
    cursor.execute("""
        SELECT champion_id, name, faction, affinity, rarity
        FROM champions
        WHERE name LIKE ?
    """, (f"%{champion_name}%",))
    
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return pd.DataFrame()
    
    champ_id, name, faction, affinity, rarity = result
    
    # Get all ratings for this champion
    cursor.execute("""
        SELECT category, subcategory, rating
        FROM ratings
        WHERE champion_id = ?
        ORDER BY category, subcategory
    """, (champ_id,))
    
    ratings = cursor.fetchall()
    conn.close()
    
    # Build a readable report format
    report_data = []
    
    # Add header row with champion info
    report_data.append({
        "Field": "Champion ID",
        "Value": champ_id
    })
    report_data.append({
        "Field": "Name",
        "Value": name
    })
    report_data.append({
        "Field": "Faction",
        "Value": faction or "N/A"
    })
    report_data.append({
        "Field": "Affinity",
        "Value": affinity or "N/A"
    })
    report_data.append({
        "Field": "Rarity",
        "Value": rarity or "N/A"
    })
    report_data.append({
        "Field": "---",
        "Value": "---"
    })
    
    # Add ratings grouped by category
    current_category = None
    for category, subcategory, rating in ratings:
        if category != current_category:
            if current_category is not None:
                report_data.append({"Field": "", "Value": ""})
            current_category = category
            report_data.append({
                "Field": f"[{category}]",
                "Value": ""
            })
        
        report_data.append({
            "Field": f"  {subcategory}",
            "Value": rating
        })
    
    df = pd.DataFrame(report_data)
    return df


def get_rating_summary_report(db_path, category=None):
    """
    Generate a report summarizing ratings by category and subcategory.
    
    Args:
        db_path: Path to the SQLite database
        category: Optional - filter by specific category
    
    Returns:
        DataFrame with rating summaries
    """
    conn = sqlite3.connect(db_path)
    
    if category:
        query = """
            SELECT c.champion_id, c.name, r.category, r.subcategory, r.rating
            FROM champions c
            JOIN ratings r ON c.champion_id = r.champion_id
            WHERE r.category = ?
            ORDER BY r.rating DESC, c.name
        """
        df = pd.read_sql_query(query, conn, params=(category,))
    else:
        query = """
            SELECT c.champion_id, c.name, r.category, r.subcategory, r.rating
            FROM champions c
            JOIN ratings r ON c.champion_id = r.champion_id
            ORDER BY r.category, r.subcategory, r.rating DESC
        """
        df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df


def get_missing_data_report(db_path):
    """
    Generate a report of champions with missing or incomplete data.
    
    Args:
        db_path: Path to the SQLite database
    
    Returns:
        DataFrame with champions missing faction, affinity, or rarity
    """
    conn = sqlite3.connect(db_path)
    
    query = """
        SELECT champion_id, name, 
               CASE WHEN faction IS NULL OR faction = '' THEN 'MISSING' ELSE 'OK' END as faction_status,
               CASE WHEN affinity IS NULL OR affinity = '' THEN 'MISSING' ELSE 'OK' END as affinity_status,
               CASE WHEN rarity IS NULL OR rarity = '' THEN 'MISSING' ELSE 'OK' END as rarity_status
        FROM champions
        WHERE faction IS NULL OR faction = '' 
           OR affinity IS NULL OR affinity = ''
           OR rarity IS NULL OR rarity = ''
        ORDER BY name
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_champion_comparison_report(db_path, category, subcategory, limit=20):
    """
    Generate a report comparing champions in a specific category/subcategory.
    
    Args:
        db_path: Path to the SQLite database
        category: Rating category (e.g., 'Core Areas')
        subcategory: Rating subcategory (e.g., 'Demon Lord')
        limit: Number of top champions to show
    
    Returns:
        DataFrame with top champions by rating
    """
    conn = sqlite3.connect(db_path)
    
    query = """
        SELECT c.champion_id, c.name, c.faction, c.affinity, c.rarity, r.rating
        FROM champions c
        JOIN ratings r ON c.champion_id = r.champion_id
        WHERE r.category = ? AND r.subcategory = ?
        ORDER BY r.rating DESC
        LIMIT ?
    """
    
    df = pd.read_sql_query(query, conn, params=(category, subcategory, limit))
    conn.close()
    return df
