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

def get_pokemon_details(pokemon_name):
    """Fetch detailed Pokémon attributes, including base stats."""
    try:
        # Normalize the Pokémon name
        normal_name = normalize_pokemon_name(pokemon_name);
        # Fetch Pokémon data
        response = requests.get(f"{API_BASE_URL}pokemon/{pokemon_name.lower()}")
        if response.status_code != 200:
            return {}

        pokemon_data = response.json()

        # Fetch species details for additional info
        species_response = requests.get(pokemon_data["species"]["url"])
        species_data = species_response.json() if species_response.status_code == 200 else {}

        # Parse relevant attributes
        legendary = species_data.get("is_legendary", False)
        starter = is_starter_pokemon(pokemon_name)
        evolution_stage = 1  # Assume basic, adjust logic for detailed evolution chains
        egg_groups = [group["name"].capitalize() for group in species_data.get("egg_groups", [])]
        height = pokemon_data["height"] / 10.0  # Convert decimetres to metres
        weight = pokemon_data["weight"] / 10.0  # Convert hectograms to kilograms

        types = [type_info["type"]["name"].capitalize() for type_info in pokemon_data["types"]]

        # Parse base stats
        base_stats = {stat["stat"]["name"]: stat["base_stat"] for stat in pokemon_data["stats"]}

        return {
            "Legendary": legendary,
            "Starter": starter,
            "Evolution Stage": evolution_stage,
            "Egg Groups": egg_groups,
            "Height": height,
            "Weight": weight,
            "Base Stats": base_stats,
            "Type": types
        }
    except Exception as e:
        print(f"Error fetching Pokémon details for {pokemon_name}: {e}")
        return {"Type": []}  # Return an empty list for missing types

def is_starter_pokemon(pokemon_name):
    """Determine if a Pokémon is part of a starter evolutionary line."""
    try:
        # Normalize the Pokémon name
        normalized_name = normalize_pokemon_name(pokemon_name)

        # Fetch Pokémon species details
        species_response = requests.get(f"{API_BASE_URL}pokemon-species/{normalized_name}")
        if species_response.status_code != 200:
            return False
        species_data = species_response.json()

        # Fetch the evolution chain
        evolution_chain_url = species_data.get("evolution_chain", {}).get("url")
        if not evolution_chain_url:
            return False
        evolution_chain_response = requests.get(evolution_chain_url)
        if evolution_chain_response.status_code != 200:
            return False
        evolution_chain_data = evolution_chain_response.json()

        # Known starter base forms
        starters = {
            "bulbasaur", "charmander", "squirtle",  # Gen 1
            "chikorita", "cyndaquil", "totodile",  # Gen 2
            "treecko", "torchic", "mudkip",        # Gen 3
            "turtwig", "chimchar", "piplup",       # Gen 4
            "snivy", "tepig", "oshawott",         # Gen 5
            "chespin", "fennekin", "froakie",     # Gen 6
            "rowlet", "litten", "popplio",        # Gen 7
            "grookey", "scorbunny", "sobble",     # Gen 8
            "eevee", "pikachu"                    # Let's Go
        }

        # Traverse the evolution chain to find all forms
        current = evolution_chain_data["chain"]
        all_forms = []
        while current:
            all_forms.append(current["species"]["name"])
            current = current["evolves_to"][0] if current["evolves_to"] else None

        # Check if any form in the chain is a known starter
        return any(form in starters for form in all_forms)
    except Exception as e:
        print(f"Error determining starter status for {pokemon_name}: {e}")
        return False

