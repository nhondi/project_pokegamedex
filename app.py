import streamlit as st
from utils.data_manager import load_data, save_data, clear_data, enrich_data
from utils.api import get_pokemon_names
from utils.visualisation import plot_pie_chart
from utils.api import get_pokemon_region, get_pokemon_details
import pandas as pd
from collections import Counter

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
    data = enrich_data(data)  # Add missing details
    save_data(data)  # Save the updated dataset

    # Sidebar: Manage Teams
    st.sidebar.header("Manage Teams")
    if not data.empty:
        grouped = data.groupby(["Game", "Playthrough"])
        for (game, playthrough), group in grouped:
            st.sidebar.write(f"**{game} Playthrough {playthrough}**")

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
        # Initialise session state for the new team
        if "new_team" not in st.session_state:
            st.session_state["new_team"] = [{"Pokemon": "None", "Acquisition": "N/A"} for _ in range(6)]

    if "new_team" in st.session_state:
        st.sidebar.write("### Enter Pokémon Details")
        for i in range(6):
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.session_state["new_team"][i]["Pokemon"] = st.selectbox(
                    f"Select Pokémon {i + 1}",
                    ["None"] + POKEMON_NAMES,
                    index=0 if st.session_state["new_team"][i]["Pokemon"] == "None"
                    else POKEMON_NAMES.index(st.session_state["new_team"][i]["Pokemon"]) + 1,
                    key=f"new_pokemon_{i}"
                )
            with col2:
                st.session_state["new_team"][i]["Acquisition"] = st.selectbox(
                    f"Acquisition {i + 1}",
                    ["N/A", "Caught", "Gifted", "Traded", "Hatched", "Other"],
                    index=0 if st.session_state["new_team"][i]["Acquisition"] == "N/A"
                    else ["Caught", "Gifted", "Traded", "Hatched", "Other"].index(
                        st.session_state["new_team"][i]["Acquisition"]
                    ) + 1,
                    key=f"new_acq_{i}"
                )

        if st.sidebar.button("Save Team"):
            for entry in st.session_state["new_team"]:
                entry.update({"Game": selected_game, "Playthrough": playthrough_number})
                
                # Fetch additional details for the Pokémon
                if entry["Pokemon"] != "None":
                    details = get_pokemon_details(entry["Pokemon"])
                    entry.update(details)
                else:
                    # Default values for None
                    entry.update({
                        "Legendary": False,
                        "Starter": False,
                        "Evolution Stage": None,
                        "Egg Groups": [],
                        "Height": None,
                        "Weight": None,
                        "Base Stats": {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
                    })
            
            data = pd.concat([data, pd.DataFrame(st.session_state["new_team"])], ignore_index=True)
            save_data(data)
            del st.session_state["new_team"]
            refresh_app()




    # Analysis Section
    if data.empty:
        st.warning("No data to analyse yet!")
    else:
        # Exclude placeholders for meaningful stats
        valid_data = data[(data["Pokemon"] != "None") & (data["Acquisition"] != "N/A")]

        # Statistical calculations
        st.subheader("General")
        total_pokemon_used = len(valid_data)
        unique_pokemon = valid_data["Pokemon"].nunique()
        total_games_played = data["Game"].nunique()
        total_playthroughs = data[["Game", "Playthrough"]].drop_duplicates().shape[0]
        avg_playthroughs_per_game = (
            total_playthroughs / total_games_played if total_games_played > 0 else 0
        )
        range_pokemon_per_playthrough = valid_data.groupby(["Game", "Playthrough"]).size().agg(["min", "max"])

        # Display statistical sentences
        st.markdown(f"""
        - **Total Pokémon used**: {total_pokemon_used}
        - **Unique Pokémon**: {unique_pokemon}
        - **Total Games Played**: {total_games_played}
        - **Playthroughs**: {total_playthroughs} (Avg: {avg_playthroughs_per_game:.2f} per game) (Range: {range_pokemon_per_playthrough['min']} - {range_pokemon_per_playthrough['max']})
        """)

        st.subheader("Pokémon Status")
        
        total_starters = valid_data["Starter"].sum()
        avg_starters_per_team = total_starters / total_playthroughs if total_playthroughs > 0 else 0

        legendary_usage = valid_data["Legendary"].sum()
        avg_legendaries_per_team = legendary_usage / total_playthroughs

        # Average Height and Weight
        avg_height = valid_data["Height"].mean()
        avg_weight = valid_data["Weight"].mean()

        st.markdown(f"""
        - **Starter Pokémon Usage**: {total_starters} (Avg: {avg_starters_per_team:.2f} per team)
        - **Legendary Pokémon Usage**: {legendary_usage} (Avg: {avg_legendaries_per_team:.2f} per team)
        - **Average Pokémon Height**: {avg_height:.2f} m
        - **Average Pokémon Weight**: {avg_weight:.2f} kg
        """)

        st.subheader("Pokemon Types")
        
        st.subheader("Pokemon Stats")

        st.subheader("Pokémon Insights")

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
