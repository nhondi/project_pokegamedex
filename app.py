import streamlit as st
from utils.data_manager import load_data, save_data, clear_data, remove_entry
from utils.api import get_pokemon_names
from utils.visualisation import plot_pie_chart
from utils.api import get_pokemon_region
import pandas as pd

# Constants
POKEMON_GAMES = [
    "Red", "Blue", "Yellow", "Gold", "Silver", "Crystal", "Ruby", "Sapphire", "Emerald",
    "FireRed", "LeafGreen", "Diamond", "Pearl", "Platinum", "HeartGold", "SoulSilver",
    "Black", "White", "Black 2", "White 2", "X", "Y", "Omega Ruby", "Alpha Sapphire",
    "Sun", "Moon", "Ultra Sun", "Ultra Moon", "Sword", "Shield", "Brilliant Diamond",
    "Shining Pearl", "Legends: Arceus", "Scarlet", "Violet"
]

# Load Pokémon names from API or fallback to a local list
POKEMON_NAMES = get_pokemon_names()

# Helper function to refresh app
def refresh_app():
    st.session_state["needs_refresh"] = True


def main():
    st.title("Pokémon Team Tracker and Analysis")

    # Load data
    data = load_data()

    # Sidebar: Manage Teams
    st.sidebar.header("Manage Teams")
    if not data.empty:
        grouped = data.groupby(["Game", "Playthrough"])
        for (game, playthrough), group in grouped:
            st.sidebar.write(f"**{game} Playthrough {playthrough}**")
            if st.sidebar.button(f"Edit Team ({game} Playthrough {playthrough})", key=f"edit_{game}_{playthrough}"):
                st.session_state["edit_team"] = (game, playthrough)
                refresh_app()

            if st.sidebar.button(f"Delete Team ({game} Playthrough {playthrough})", key=f"delete_{game}_{playthrough}"):
                data = data[(data["Game"] != game) | (data["Playthrough"] != playthrough)]
                save_data(data)
                refresh_app()

    if st.sidebar.button("Clear All Data"):
        clear_data()
        refresh_app()

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
            refresh_app()

    # Edit Team
    if "edit_team" in st.session_state:
        game, playthrough = st.session_state["edit_team"]
        team_data = data[(data["Game"] == game) & (data["Playthrough"] == playthrough)]
        st.write(f"### Edit Team: {game} (Playthrough {playthrough})")

        updated_team = []  # To hold the modified team data
        for idx, row in team_data.iterrows():
            col1, col2, col3 = st.columns(3)
            with col1:
                # Replace text input with dropdown for Pokémon names
                selected_pokemon = st.selectbox(
                    "Select Pokémon",
                    POKEMON_NAMES,
                    index=POKEMON_NAMES.index(row["Pokemon"]) if row["Pokemon"] in POKEMON_NAMES else 0,
                    key=f"edit_pokemon_{idx}"
                )
            with col2:
                # Acquisition method dropdown
                acquisition_method = st.selectbox(
                    "Acquisition Method",
                    ["Caught", "Gifted", "Traded", "Hatched", "Other"],
                    index=["Caught", "Gifted", "Traded", "Hatched", "Other"].index(row["Acquisition"]),
                    key=f"edit_acq_{idx}"
                )
            with col3:
                # Remove option
                if st.button("Remove", key=f"remove_{idx}"):
                    continue  # Skip this Pokémon if "Remove" is clicked
            updated_team.append({
                "Game": game,
                "Playthrough": playthrough,
                "Pokemon": selected_pokemon,
                "Acquisition": acquisition_method
            })

        # Save the updated team
        if st.button("Save Changes"):
            # Remove the old team data and replace with the updated team
            data = data[(data["Game"] != game) | (data["Playthrough"] != playthrough)]
            data = pd.concat([data, pd.DataFrame(updated_team)], ignore_index=True)
            save_data(data)
            st.session_state.pop("edit_team")
            refresh_app()  # Refresh the app after saving changes

    # Analysis Section
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

        # Regional Analysis
        st.header("Regional Analysis")
        if data.empty:
            st.warning("No data to analyse yet!")
        else:
            # Fetch region for each Pokémon
            data["Region"] = data["Pokemon"].apply(get_pokemon_region)

            # Count Pokémon by region
            region_counts = data["Region"].value_counts()

            # Display analysis
            st.subheader("Pokémon Distribution by Region (Pie Chart)")
            plot_pie_chart(region_counts, "Regional Distribution of Pokémon")

            st.subheader("Detailed Regional Data")
            st.write(data[["Pokemon", "Region"]])

if __name__ == "__main__":
    main()
