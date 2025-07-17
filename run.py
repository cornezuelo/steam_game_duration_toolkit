"""
CLI launcher for the Steam Game‑Duration Toolkit.

Precedence order
1. Explicit CLI flag   (e.g. --debug / --no-debug / --all)
2. Value in .env       (HLTB_DEBUG, FILTER_UNPLAYED …)
3. Hard‑coded default  (see config.py)
"""

import argparse
from typing import Optional

from steam_toolkit.config import (
    STEAM_API_KEY,
    STEAM_ID64,
    MAX_DURATION,
    LIMIT,
    FILTER_UNPLAYED,
    EXPORT_TO_CSV,
    HLTB_DEBUG,
    USE_CACHE,
    HLTB_MIN_SIMILARITY,
)
from steam_toolkit.combine import run as analyse


# ── helpers ────────────────────────────────────────────────────────────
def _tri(cli_true: bool, cli_false: bool, env_default: bool) -> bool:
    """CLI true wins > CLI false > env default."""
    return True if cli_true else False if cli_false else env_default


def _intval(cli_val: Optional[int], env_default: int) -> int:
    return cli_val if cli_val is not None else env_default


# ── CLI definition ─────────────────────────────────────────────────────
p = argparse.ArgumentParser("Steam game‑duration analyzer")

p.add_argument("--duration", type=int, help="Max main‑story hours (<=)")
p.add_argument("--limit",    type=int, help="Max games to process (0 = all)")

p.add_argument("--csv",     action="store_true", help="Enable CSV export")
p.add_argument("--no-csv",  action="store_true", help="Disable CSV export")

p.add_argument("--unplayed", action="store_true", help="Only unplayed games")
p.add_argument("--all",      action="store_true", help="Include played games")

p.add_argument("--debug",    action="store_true", help="Show HLTB debug logs")
p.add_argument("--no-debug", action="store_true", help="Hide debug logs")

p.add_argument("--cache",    action="store_true", help="Use local HLTB cache")
p.add_argument("--no-cache", action="store_true", help="Ignore / rebuild cache")

p.add_argument(
    "--sim",
    type=float,
    help="Min similarity 0‑1 (overrides env HLTB_MIN_SIMILARITY)",
)

cli = p.parse_args()


# ── effective values ──────────────────────────────────────────────────
export_csv = _tri(cli.csv,   cli.no_csv,  EXPORT_TO_CSV)
debug      = _tri(cli.debug, cli.no_debug, HLTB_DEBUG)
use_cache  = _tri(cli.cache, cli.no_cache, USE_CACHE)
min_sim    = cli.sim if cli.sim is not None else HLTB_MIN_SIMILARITY

# handle unplayed / all logic
if cli.all:
    only_unplayed = False
else:
    only_unplayed = cli.unplayed if cli.unplayed else FILTER_UNPLAYED


# ── run analysis ───────────────────────────────────────────────────────
analyse(
    steam_id       = STEAM_ID64,
    api_key        = STEAM_API_KEY,
    max_duration   = _intval(cli.duration, MAX_DURATION),
    limit          = _intval(cli.limit,    LIMIT),
    only_unplayed  = only_unplayed,
    export_csv     = export_csv,
    debug          = debug,
    use_cache      = use_cache,
    min_similarity      = min_sim
)

if __name__ == "__main__":
    pass  # argparse already executed
