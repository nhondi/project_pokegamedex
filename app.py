import streamlit as st
from utils.data_manager import load_data, save_data, clear_data, remove_entry
from utils.api import get_pokemon_names
from utils.visualisation import plot_pie_chart
import pandas as pd

# Constants
POKEMON_GAMES = [
    "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal", "Ruby", "Sapphire", "Emerald",
    "FireRed", "LeafGreen", "Diamond", "Pearl", "Platinum", "HeartGold", "SoulSilver",
    "Black", "White", "Black 2", "White 2", "X", "Y", "Omega Ruby", "Alpha Sapphire",
    "Sun", "Moon", "Ultra Sun", "Ultra Moon", "Sword", "Shield", "Brilliant Diamond",
    "Shining Pearl", "Legends: Arceus", "Scarlet", "Violet"
]

# Load Pokémon names from API or local fallback
POKEMON_NAMES = get_pokemon_names()

def main():
    st.title("Pokémon Team Tracker and Analysis")

    # Load data
    data = load_data()

    # Sidebar: Manage Teams
    st.sidebar.header("Manage Teams")
    if not data.empty:
        st.sidebar.write("### Current Teams")
        for idx, row in data.iterrows():
            st.sidebar.write(f"{row['Game']} (Playthrough {row['Playthrough']}): {row['Pokemon']} [{row['Acquisition']}]")
            if st.sidebar.button(f"Remove Entry {idx}", key=f"remove_{idx}"):
                remove_entry(idx)
                st.session_state["needs_refresh"] = True

    if st.sidebar.button("Clear All Data"):
        clear_data()
        st.session_state["needs_refresh"] = True

    # Add New Team
    st.sidebar.write("### Add New Team")
    selected_game = st.sidebar.selectbox("Select Game", POKEMON_GAMES, help="Start typing to search for a game.")
    playthrough_number = st.sidebar.number_input("Playthrough Number", min_value=1, step=1)

    if st.sidebar.button("Add Team"):
        st.session_state["add_team"] = True

    if st.session_state.get("add_team", False):
        st.sidebar.write("### Enter Pokémon Details")
        new_team = []
        for i in range(6):
            col1, col2 = st.sidebar.columns(2)
            with col1:
                selected_pokemon = st.selectbox(
                    f"Select Pokémon {i + 1}",
                    POKEMON_NAMES,
                    key=f"pokemon_{i}",
                    help="Start typing to search for a Pokémon."
                )
            with col2:
                acquisition_method = st.selectbox(
                    f"Acquisition {i + 1}",
                    ["Caught", "Gifted", "Traded", "Hatched", "Other"],
                    key=f"acquisition_{i}"
                )
            if selected_pokemon:
                new_team.append({
                    "Game": selected_game,
                    "Playthrough": playthrough_number,
                    "Pokemon": selected_pokemon,
                    "Acquisition": acquisition_method
                })

        if len(new_team) == 6 and st.sidebar.button("Save Team"):
            data = pd.concat([data, pd.DataFrame(new_team)], ignore_index=True)
            save_data(data)
            st.session_state["add_team"] = False
            st.session_state["needs_refresh"] = True

    # Main Analysis Section
    st.header("Team Analysis")
    if data.empty:
        st.warning("No data to analyse yet!")
    else:
        # Most Common Pokémon
        st.subheader("Most Common Pokémon")
        most_common = data["Pokemon"].value_counts().head(5)
        st.bar_chart(most_common)

        # Acquisition Breakdown
        st.subheader("Acquisition Breakdown")
        acquisition_counts = data["Acquisition"].value_counts()
        st.bar_chart(acquisition_counts)

if __name__ == "__main__":
    main()
