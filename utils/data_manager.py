import os
import pandas as pd
from utils.api import get_pokemon_details
DATA_FILE = "data/teams.csv"

def enrich_data(data):
    """Enrich the dataset with additional Pokémon details."""
    enriched_rows = []
    for _, row in data.iterrows():
        # Skip rows where Pokémon is 'None'
        if row["Pokemon"] == "None":
            enriched_rows.append(row)
            continue

        # Fetch details if missing
        details = get_pokemon_details(row["Pokemon"])
        for key, value in details.items():
            row[key] = row.get(key, value)  # Update only if missing
        enriched_rows.append(row)

    return pd.DataFrame(enriched_rows)


def load_data():
    """Load team data from CSV or create an empty structure if missing."""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Game", "Playthrough", "Pokemon", "Acquisition"])
    
    try:
        data = pd.read_csv(DATA_FILE)
        required_columns = ["Game", "Playthrough", "Pokemon", "Acquisition"]
        for column in required_columns:
            if column not in data.columns:
                data[column] = None
        return data
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=["Game", "Playthrough", "Pokemon", "Acquisition"])

def save_data(data):
    """Save team data to CSV."""
    data.to_csv(DATA_FILE, index=False)

def clear_data():
    """Clear all team data."""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def remove_entry(index):
    """Remove a specific entry by index."""
    data = load_data()
    if index in data.index:
        data = data.drop(index)
        save_data(data)
