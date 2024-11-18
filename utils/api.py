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
