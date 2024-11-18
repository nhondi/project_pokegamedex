import requests

API_BASE_URL = "https://pokeapi.co/api/v2/"

def get_pokemon_names(limit=1000):
    """Fetch a list of Pokémon names from PokeAPI."""
    try:
        response = requests.get(f"{API_BASE_URL}pokemon?limit={limit}")
        if response.status_code == 200:
            pokemon_list = response.json()["results"]
            return [pokemon["name"].capitalize() for pokemon in pokemon_list]
    except Exception as e:
        print(f"Error fetching Pokémon names: {e}")

def get_pokemon_region(pokemon_name):
    """Fetch the region for a specific Pokémon."""
    try:
        # Normalize the Pokémon name
        normalized_name = normalize_pokemon_name(pokemon_name)

        # Query the Pokémon species endpoint
        species_url = f"{API_BASE_URL}pokemon-species/{normalized_name}"
        response = requests.get(species_url)
        if response.status_code == 200:
            species_data = response.json()
            region = species_data.get("generation", {}).get("name", "Unknown")
            return region.capitalize()
    except Exception as e:
        print(f"Error fetching region for Pokémon {pokemon_name}: {e}")
    return "Unknown"


def normalize_pokemon_name(name):
    """Normalize Pokémon names to match the API's naming conventions."""
    # Handle specific cases where forms or descriptors are appended
    form_mappings = {
        "darmanitan-standard": "darmanitan",
        "giratina-altered": "giratina",
        "wormadam-plant": "wormadam",
        # Add more mappings as necessary
    }
    normalized_name = form_mappings.get(name.lower(), name.lower())
    return normalized_name

