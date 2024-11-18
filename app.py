import streamlit as st
from utils.data_manager import load_data, save_data, clear_data, enrich_data
from utils.api import get_pokemon_names
from utils.visualisation import plot_pie_chart, plot_scatter, plot_histogram, plot_bar, plot_box, plot_heatmap, plot_boxen, plot_grouped_bar, plot_kde, plot_pair, plot_radar, plot_violin
from utils.api import get_pokemon_region, get_pokemon_details
import pandas as pd
import plotly.express as px

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
        regional_analysis(valid_data)
        type_analysis(valid_data)      
        stats_analysis(valid_data)
        insight_analysis(valid_data)

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

        type_insights = generate_type_insights(valid_data)
        for insight in type_insights:
            st.markdown(f"- {insight}")

        # Explode types for independent analysis
        exploded_types = valid_data.explode("Type")

        # Most Common Type
        type_counts = exploded_types["Type"].value_counts()
        # Type Pie Chart
        st.subheader("Type Distribution")
        col1, col2 = st.columns(2)
        if not type_counts.empty:
            with col1:
                plot_pie_chart(type_counts, "Type Distribution")
                
            with col2:
                plot_grouped_bar(valid_data.explode("Type"), category_col="Type", 
                title="Pokémon Counts by Type", x_label="Type", y_label="Count")

        # Type Coverage Per Team
        unique_types_per_team = valid_data.groupby(["Game", "Playthrough"])["Type"].apply(
            lambda types: len(set(t for sublist in types if isinstance(sublist, list) for t in sublist))
        )
        st.markdown("**Type Coverage Per Team**")
        st.table(unique_types_per_team.reset_index(name="Unique Types"))

        # Average Types Per Playthrough
        average_types_per_playthrough = unique_types_per_team.mean()
        st.markdown(f"**Average Types Per Playthrough**: {average_types_per_playthrough:.2f}")
def generate_type_insights(valid_data):
    """Generate insights related to Pokémon types."""
    insights = []
    # Explode types for analysis
    exploded_types = valid_data.explode("Type")

    # Most Common Type
    type_counts = exploded_types["Type"].value_counts()
    if not type_counts.empty:
        most_common_type = type_counts.idxmax()
        most_common_type_count = type_counts.max()
        insights.append(f"The most common type is {most_common_type}, appearing {most_common_type_count} times.")

    # Starter Pokémon Type Analysis
    starter_data = valid_data[valid_data["Starter"]]
    exploded_starter_types = starter_data.explode("Type")
    if not exploded_starter_types.empty:
        starter_type_counts = exploded_starter_types["Type"].value_counts()
        most_common_starter_type = starter_type_counts.idxmax()
        most_common_starter_type_count = starter_type_counts.max()
        insights.append(f"The most common starter type is {most_common_starter_type}, appearing {most_common_starter_type_count} times among starter Pokémon.")

    # Type Coverage Insights
    unique_types_per_team = valid_data.groupby(["Game", "Playthrough"])["Type"].apply(
        lambda types: len(set(t for sublist in types if isinstance(sublist, list) for t in sublist))
    )
    if not unique_types_per_team.empty:
        average_types_per_playthrough = unique_types_per_team.mean()
        insights.append(f"On average, teams cover {average_types_per_playthrough:.2f} unique types per playthrough.")

    return insights

def stats_analysis(valid_data):
    st.subheader("Pokemon Stats")

def insight_analysis(valid_data):
    st.subheader("Other Pokémon Insights")
    height_weight_insights = generate_height_weight_insights(valid_data)
    for insight in height_weight_insights:
        st.markdown(f"- {insight}")

    box1, box2 = st.columns(2)
    with box1:
        # Height Box Plot
        plot_box(valid_data, column="Height", 
            title="Pokémon Height Spread", 
            y_label="Height (m)")
        
    with box2:
        # Weight Box Plot
        plot_box(valid_data, column="Weight", 
            title="Pokémon Weight Spread", 
            y_label="Weight (kg)")

    plot_scatter(valid_data, x_col="Height", y_col="Weight", 
             title="Height vs Weight", 
             x_label="Height (m)", 
             y_label="Weight (kg)")

    histo1, histo2 = st.columns(2)
    with histo1:
        # Height Histogram
        plot_histogram(valid_data, column="Height", 
               title="Height Distribution (Histogram)", 
               x_label="Height (m)")

    with histo2:
        # Weight Histogram
        plot_histogram(valid_data, column="Weight", 
               title="Weight Distribution (Histogram)", 
               x_label="Weight (kg)")
        
    kde1, kde2 = st.columns(2)
    with kde1:
        plot_kde(valid_data, column="Height", title="Height Distribution (KDE)", x_label="Height (m)")
    with kde2:
        plot_kde(valid_data, column="Weight", title="Weight Distribution (KDE)", x_label="Weight (kg)")
def generate_height_weight_insights(data):
    """Generate textual insights from height and weight statistics."""
    insights = []

    if data.empty:
        insights.append("No data available to generate height and weight insights.")
        return insights

    # Height statistics
    tallest_pokemon = data.loc[data["Height"].idxmax()]
    shortest_pokemon = data.loc[data["Height"].idxmin()]
    avg_height = data["Height"].mean()
    median_height = data["Height"].median()
    std_height = data["Height"].std()

    # Weight statistics
    heaviest_pokemon = data.loc[data["Weight"].idxmax()]
    lightest_pokemon = data.loc[data["Weight"].idxmin()]
    avg_weight = data["Weight"].mean()
    median_weight = data["Weight"].median()
    std_weight = data["Weight"].std()

    # Add insights
    insights.append(f"The tallest Pokémon used is {tallest_pokemon['Pokemon']} at {tallest_pokemon['Height']:.2f} m, while the shortest is {shortest_pokemon['Pokemon']} at {shortest_pokemon['Height']:.2f} m.")
    insights.append(f"The heaviest Pokémon used is {heaviest_pokemon['Pokemon']} at {heaviest_pokemon['Weight']:.2f} kg, while the lightest is {lightest_pokemon['Pokemon']} at {lightest_pokemon['Weight']:.2f} kg.")
    insights.append(f"On average, Pokémon are {avg_height:.2f} m tall and weigh {avg_weight:.2f} kg.")
    insights.append(f"The median height is {median_height:.2f} m, and the median weight is {median_weight:.2f} kg.")
    insights.append(f"The standard deviation in height is {std_height:.2f} m, and in weight is {std_weight:.2f} kg.")

    # Add range-based insights
    most_common_height_range = f"{max(0, median_height - std_height):.2f} m to {median_height + std_height:.2f} m"
    most_common_weight_range = f"{max(0, median_weight - std_weight):.2f} kg to {median_weight + std_weight:.2f} kg"
    insights.append(f"Most Pokémon fall within the height range of {most_common_height_range}.")
    insights.append(f"Most Pokémon weigh between {most_common_weight_range}.")

    # Add correlation if possible
    correlation = data["Height"].corr(data["Weight"])
    if not pd.isna(correlation):
        correlation_strength = "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.4 else "weak"
        insights.append(f"There is a {correlation_strength} correlation ({correlation:.2f}) between height and weight, indicating that larger Pokémon tend to be heavier.")

    return insights

def regional_analysis(valid_data):
    # Fetch region for each Pokémon
    valid_data["Region"] = valid_data["Pokemon"].apply(get_pokemon_region)

    # Regional Analysis
    st.header("Regional Analysis")
    region_insights = generate_region_insights(valid_data)
    for insight in region_insights:
        st.markdown(f"- {insight}")

    # Count Pokémon by region
    region_counts = valid_data["Region"].value_counts()

    # Display analysis
    col1, col2 = st.columns(2)
    with col1:
        plot_pie_chart(region_counts, "Regional Distribution of Pokémon")
    with col2:
        plot_bar(region_counts, title="Pokémon Counts by Region", x_label="Region", y_label="Count")

def generate_region_insights(data):
    """Generate insights from regional Pokémon data."""
    insights = []

    # Check if the dataset is empty
    if data.empty or "Region" not in data.columns:
        insights.append("No regional data available for analysis.")
        return insights

    # Count Pokémon by region
    region_counts = data["Region"].value_counts()

    # Total Pokémon and unique regions
    total_pokemon = region_counts.sum()
    unique_regions = region_counts.index.nunique()

    # Most and least common regions
    most_common_region = region_counts.idxmax()
    most_common_count = region_counts.max()
    least_common_region = region_counts.idxmin()
    least_common_count = region_counts.min()

    # Percentage contribution of the most common region
    most_common_percentage = (most_common_count / total_pokemon) * 100

    # Add insights
    insights.append(f"A total of {total_pokemon} Pokémon are distributed across {unique_regions} regions.")
    insights.append(f"The most common region is {most_common_region} with {most_common_count} Pokémon, making up {most_common_percentage:.2f}% of the total.")
    insights.append(f"The least common region is {least_common_region} with only {least_common_count} Pokémon.")

    # Optional: Highlight even distribution
    avg_pokemon_per_region = total_pokemon / unique_regions
    if least_common_count < avg_pokemon_per_region * 0.5:
        insights.append(f"There is a significant imbalance, with {least_common_region} having much fewer Pokémon than the average of {avg_pokemon_per_region:.2f} per region.")

    return insights

if __name__ == "__main__":
    main()
