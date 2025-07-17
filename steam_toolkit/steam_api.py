"""
Fetches game data from the Steam Web API, including playtime and metadata.
"""

import requests
from dataclasses import dataclass
from typing import List


@dataclass
class SteamGame:
    appid: int
    name: str
    playtime_forever: int  # minutes
    playtime_recent: int   # minutes
    img_logo_url: str
    has_community_visible_stats: bool


def get_owned_games(steam_id: str, api_key: str) -> List[SteamGame]:
    """
    Fetch all games owned by a Steam user using their SteamID64 and API key.
    Returns a list of SteamGame objects.
    """
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True,
        "format": "json"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    games_data = data.get("response", {}).get("games", [])
    games = []

    for game in games_data:
        games.append(SteamGame(
            appid=game.get("appid"),
            name=game.get("name"),
            playtime_forever=game.get("playtime_forever", 0),
            playtime_recent=game.get("playtime_2weeks", 0),
            img_logo_url=game.get("img_logo_url", ""),
            has_community_visible_stats=game.get("has_community_visible_stats", False)
        ))

    return games
