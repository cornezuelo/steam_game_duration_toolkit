"""
Core analysis logic: scan Steam library, enrich with HLTB durations,
filter by max hours and (optionally) unplayed status.
"""

from time import sleep
from typing import List, Tuple
import csv

from steam_toolkit.steam_api import get_owned_games
from steam_toolkit.hltb_api import search_game_duration
from steam_toolkit.hltb_cache import (
    load_cache,
    save_cache,
    duration_from_cache,
    cache_duration,
)
from steam_toolkit.filters import filter_unplayed


def _print_game(name: str, d, cached: bool) -> None:
    tag = "[CACHE]" if cached else "[LIVE]"
    print(f"{name} {tag}")
    print(f"  • Main : {d.main_story} h")
    print(f"  • Extra: {d.main_extra} h")
    print(f"  • 100% : {d.completionist} h\n")


def run(  # noqa: C901
    steam_id: str,
    api_key: str,
    max_duration: int,
    limit: int,
    only_unplayed: bool,
    export_csv: bool,
    debug: bool,
    use_cache: bool,
) -> None:
    games = get_owned_games(steam_id, api_key)

    if only_unplayed:
        games = filter_unplayed(games)

    if limit > 0:
        games = games[:limit]

    cache = load_cache() if use_cache else {}
    short_games: List[Tuple[str, object, bool]] = []

    print(f"\nSearching games with main story ≤ {max_duration} h …\n")

    for g in games:
        cached = False
        duration = duration_from_cache(g.name, cache) if use_cache else None

        if duration:
            cached = True
        else:
            duration = search_game_duration(g.name, debug=debug)
            if duration and use_cache:
                cache_duration(g.name, duration, cache)
            if not cached:  # throttle only on live look‑ups
                sleep(1.0)

        if duration and duration.main_story and duration.main_story <= max_duration:
            short_games.append((g.name, duration, cached))

    if use_cache:
        save_cache(cache)

    # ── output ───────────────────────────────────────────────────────────
    short_games.sort(key=lambda x: x[0])
    for name, d, cached in short_games:
        _print_game(name, d, cached)

    if export_csv and short_games:
        with open("filtered_games.csv", "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(
                ["Title", "Main Story", "Main + Extra", "Completionist", "From Cache"]
            )
            for name, d, cached in short_games:
                wr.writerow([name, d.main_story, d.main_extra, d.completionist, cached])
        print("🎉  Exported to filtered_games.csv")
