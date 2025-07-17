"""
Core analysis logic:
• pull Steam library
• enrich each title with HowLongToBeat durations
• filter by max main‑story hours (≤ max_duration)
• optional CSV export for matched and unmatched titles
"""

from __future__ import annotations

from time import sleep
from csv import writer
from typing import List, Tuple

from steam_toolkit.steam_api import get_owned_games
from steam_toolkit.filters import filter_unplayed
from steam_toolkit.hltb_api import search_game_duration
from steam_toolkit.hltb_cache import (
    load_cache,
    save_cache,
    duration_from_cache,
    cache_duration,
)


# ── helper ────────────────────────────────────────────────────────────
def _print_game(title: str, dur, cached: bool) -> None:
    tag = "[CACHE]" if cached else "[LIVE]"
    print(f"{title} {tag}\n  • Main : {dur.main_story} h\n")


# ── main entry ────────────────────────────────────────────────────────
def run(
    *,
    steam_id: str,
    api_key: str,
    max_duration: int,
    limit: int,
    only_unplayed: bool,
    export_csv: bool,
    debug: bool,
    use_cache: bool,
    min_similarity: float,
) -> None:
    """Fetch → enrich → filter → print → CSV."""
    # 1) obtain library --------------------------------------------------
    games = get_owned_games(steam_id, api_key)
    if only_unplayed:
        games = filter_unplayed(games)
    if limit > 0:
        games = games[:limit]

    # 2) prepare cache ---------------------------------------------------
    cache = load_cache() if use_cache else {}
    matched: List[Tuple[str, object, bool]] = []
    unmatched: List[str] = []

    print(f"\nSearching games with main story ≤ {max_duration} h …\n")

    # 3) iterate games ---------------------------------------------------
    for g in games:
        dur = duration_from_cache(g.name, cache) if use_cache else None
        cached = dur is not None

        if not dur:
            dur = search_game_duration(
                g.name, debug=debug, min_similarity=min_similarity
            )
            if dur and use_cache:
                cache_duration(g.name, dur, cache)
            if not cached:
                sleep(1.0)  # throttle live look‑ups

        if dur and dur.main_story and dur.main_story <= max_duration:
            matched.append((g.name, dur, cached))
        elif dur is None:
            unmatched.append(g.name)

    # 4) persist cache ---------------------------------------------------
    if use_cache:
        save_cache(cache)

    # 5) console output --------------------------------------------------
    matched.sort(key=lambda x: x[0].lower())
    for title, dur, cached in matched:
        _print_game(title, dur, cached)

    # 6) CSV export ------------------------------------------------------
    if export_csv:
        if matched:
            with open("filtered_games.csv", "w", newline="", encoding="utf-8") as f:
                w = writer(f)
                w.writerow(["Title", "Main", "Extra", "100%", "FromCache"])
                for t, d, c in matched:
                    w.writerow([t, d.main_story, d.main_extra, d.completionist, c])
        if unmatched:
            with open("unmatched_games.csv", "w", newline="", encoding="utf-8") as f:
                writer(f).writerows([[u] for u in unmatched])
