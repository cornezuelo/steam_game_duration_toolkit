"""
Utility functions to filter and sort Steam games by playtime.
"""

from typing import List
from .steam_api import SteamGame


def filter_unplayed(games: List[SteamGame]) -> List[SteamGame]:
    """
    Return only games that have never been played (0 minutes).
    """
    return [game for game in games if game.playtime_forever == 0]


def filter_played_less_than(games: List[SteamGame], max_hours: float) -> List[SteamGame]:
    """
    Return games played less than or equal to max_hours.
    """
    max_minutes = max_hours * 60
    return [game for game in games if game.playtime_forever <= max_minutes]


def sort_by_playtime(games: List[SteamGame], descending: bool = False) -> List[SteamGame]:
    """
    Return games sorted by total playtime (ascending or descending).
    """
    return sorted(games, key=lambda g: g.playtime_forever, reverse=descending)
