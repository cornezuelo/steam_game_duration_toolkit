"""
Simple JSON-based cache for storing HowLongToBeat results locally.

This avoids unnecessary API calls and improves performance.
"""

import json
from pathlib import Path
from typing import Optional, Dict
from steam_toolkit.hltb_api import GameDuration as HltbGameDuration

CACHE_FILE = Path("hltb_cache.json")


def load_cache() -> Dict[str, dict]:
    """
    Load the local cache file into memory.
    If the file is missing or corrupted, create a new empty one.
    """
    if CACHE_FILE.exists():
        try:
            with CACHE_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[WARNING] Cache file is corrupted. Replacing with empty cache.")
            save_cache({})
            return {}
    return {}


def save_cache(cache: dict) -> None:
    """
    Save the current cache to disk as JSON.
    """
    with CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def duration_from_cache(name: str, cache: dict) -> Optional[HltbGameDuration]:
    """
    Retrieve a GameDuration from the cache by name, or None if not found.
    """
    if name not in cache:
        return None

    data = cache[name]
    return HltbGameDuration(
        name=data.get("name", name),
        main_story=data.get("main_story"),
        main_extra=data.get("main_extra"),
        completionist=data.get("completionist"),
    )


def cache_duration(name: str, duration: HltbGameDuration, cache: dict) -> None:
    """
    Store a GameDuration in the cache under the given name.
    """
    cache[name] = {
        "name": duration.name,
        "main_story": duration.main_story,
        "main_extra": duration.main_extra,
        "completionist": duration.completionist,
    }
