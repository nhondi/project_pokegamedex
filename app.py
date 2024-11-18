import streamlit as st
from utils.data_manager import load_data, save_data, clear_data, enrich_data
from utils.api import get_pokemon_names
from utils.visualisation import plot_pie_chart
from utils.api import get_pokemon_region, get_pokemon_details
import pandas as pd
import plotly.express as px
from matplotlib import pyplot as plt

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

    data = initialise()

    sidebar(data);

    # Analysis Section
    if data.empty:
        st.warning("No data to analyse yet!")
    else:
        # Exclude placeholders for meaningful stats
        valid_data = data[(data["Pokemon"] != "None") & (data["Acquisition"] != "N/A")]
        
        total_playthroughs = general_analysis(valid_data, data)
        status_analysis(valid_data, total_playthroughs)
        type_analysis(valid_data)      
        stats_analysis(valid_data)
        insight_analysis()
        regional_analysis(valid_data)

        # Acquisition Breakdown
        st.subheader("Acquisition Breakdown")
        acquisition_counts = valid_data["Acquisition"].value_counts()
        st.bar_chart(acquisition_counts)

        

def initialise():
    # Load data
    data = load_data()
    data = enrich_data(data)  # Add missing details
    save_data(data)  # Save the updated dataset
    return data

def sidebar(data):
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
                        "Base Stats": {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
                        "Type": []
                    })
            
            data = pd.concat([data, pd.DataFrame(st.session_state["new_team"])], ignore_index=True)
            save_data(data)
            del st.session_state["new_team"]
            refresh_app()

def general_analysis(valid_data, data):
    # Statistical calculations
        st.subheader("General")
        total_pokemon_used = len(valid_data)
        unique_pokemon = valid_data["Pokemon"].nunique()
        total_games_played = data["Game"].nunique()
        total_playthroughs = data[["Game", "Playthrough"]].drop_duplicates().shape[0]
        avg_playthroughs_per_game = (
            total_playthroughs / total_games_played if total_games_played > 0 else 0
        )

        # Display statistical sentences
        st.markdown(f"""
        - **Total Pokémon used**: {total_pokemon_used} (Unique: {unique_pokemon})
        - **Total Games Played**: {total_games_played}
        - **Total Playthroughs**: {total_playthroughs} (Avg: {avg_playthroughs_per_game:.2f} per game)
        """)

        # Most Commonly Used Pokemon
        pokemon_counts = valid_data["Pokemon"].value_counts().head(10).reset_index()
        pokemon_counts.columns = ["Pokémon", "Count"]

        # Create interactive bar chart
        fig = px.bar(pokemon_counts, x="Pokémon", y="Count", title="Top 10 Most Commonly Used Pokémon")
        st.plotly_chart(fig)

        return total_playthroughs;

def status_analysis(valid_data, total_playthroughs):
    st.subheader("Pokémon Status")
        
    total_starters = valid_data["Starter"].sum()
    avg_starters_per_team = total_starters / total_playthroughs if total_playthroughs > 0 else 0

    legendary_usage = valid_data["Legendary"].sum()
    avg_legendaries_per_team = legendary_usage / total_playthroughs

    st.markdown(f"""
        - **Starter Pokémon Usage**: {total_starters} (Avg: {avg_starters_per_team:.2f} per team)
        - **Legendary Pokémon Usage**: {legendary_usage} (Avg: {avg_legendaries_per_team:.2f} per team)
        """)

def type_analysis(valid_data):
    st.subheader("Pokémon Type Analysis")
    # Explode types for valid data
    if "Type" in valid_data.columns:
        valid_data["Type"] = valid_data["Type"].apply(lambda x: eval(x) if isinstance(x, str) else x)

        # Explode types for independent analysis
        exploded_types = valid_data.explode("Type")

        # Most Common Type
        type_counts = exploded_types["Type"].value_counts()
        most_common_type = type_counts.idxmax()
        st.markdown(f"**Most Common Type**: {most_common_type} ({type_counts.max()} occurrences)")

        # Most Common Starter Type
        # Ensure "Starter" column is boolean and fill NaN with False
        valid_data["Starter"] = valid_data["Starter"].fillna(False).astype(bool)

        # Filter data for starter Pokémon
        starter_data = valid_data[valid_data["Starter"]]
        exploded_starter_types = starter_data.explode("Type")
        if not exploded_starter_types.empty:
            starter_type_counts = exploded_starter_types["Type"].value_counts()
            most_common_starter_type = starter_type_counts.idxmax()
            st.markdown(f"**Most Common Starter Type**: {most_common_starter_type} ({starter_type_counts.max()} occurrences)")

        # Type Pie Chart
        st.subheader("Type Distribution (Pie Chart)")
        if not type_counts.empty:
            plot_pie_chart(type_counts, "Type Distribution")

        # Type Coverage Per Team
        unique_types_per_team = valid_data.groupby(["Game", "Playthrough"])["Type"].apply(
            lambda types: len(set(t for sublist in types if isinstance(sublist, list) for t in sublist))
        )
        st.markdown("**Type Coverage Per Team**")
        st.table(unique_types_per_team.reset_index(name="Unique Types"))

        # Average Types Per Playthrough
        average_types_per_playthrough = unique_types_per_team.mean()
        st.markdown(f"**Average Types Per Playthrough**: {average_types_per_playthrough:.2f}")

def stats_analysis(valid_data):
    st.subheader("Pokemon Stats")
    # Average Height and Weight
    avg_height = valid_data["Height"].mean()
    avg_weight = valid_data["Weight"].mean()

    st.markdown(f"""
    - **Average Pokémon Height**: {avg_height:.2f} m
    - **Average Pokémon Weight**: {avg_weight:.2f} kg
    """)

def insight_analysis():
    st.subheader("Other Pokémon Insights")

def regional_analysis(valid_data):
    # Regional Analysis
    st.header("Regional Analysis")
    # Fetch region for each Pokémon
    valid_data["Region"] = valid_data["Pokemon"].apply(get_pokemon_region)

    # Count Pokémon by region
    region_counts = valid_data["Region"].value_counts()

    # Display analysis
    st.subheader("Pokémon Distribution by Region (Pie Chart)")
    plot_pie_chart(region_counts, "Regional Distribution of Pokémon")

    st.subheader("Detailed Regional Data")
    st.write(valid_data[["Pokemon", "Region"]])

if __name__ == "__main__":
    main()
