import os
import pandas as pd

DATA_FILE = "data/teams.csv"

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
