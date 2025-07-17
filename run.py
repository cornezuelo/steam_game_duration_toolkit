"""
CLI launcher for the Steam Game‑Duration Toolkit.

Flag precedence
---------------
1. explicit CLI flag             (--debug / --no-debug / --csv / --no-csv …)
2. value in .env                 (HLTB_DEBUG, EXPORT_TO_CSV, USE_CACHE …)
3. hard‑coded default            (see config.py)
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
)
from steam_toolkit.combine import run as analyse


# ── helpers ──────────────────────────────────────────────────────────────
def _tri_state(cli_true: bool, cli_false: bool, env_default: bool) -> bool:
    """CLI true wins > CLI false > env default."""
    if cli_true:
        return True
    if cli_false:
        return False
    return env_default


def _int(cli_val: Optional[int], default: int) -> int:
    return cli_val if cli_val is not None else default


# ── CLI definition ───────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Steam game‑duration analyzer")

parser.add_argument("--duration", type=int, help="Max main‑story hours (<=)")
parser.add_argument("--limit",    type=int, help="Max games to process (0 = all)")

parser.add_argument("--csv",     action="store_true", help="Enable CSV export")
parser.add_argument("--no-csv",  action="store_true", help="Disable CSV export")

parser.add_argument("--unplayed", action="store_true", help="Only unplayed games")

parser.add_argument("--debug",    action="store_true", help="Enable HLTB debug logs")
parser.add_argument("--no-debug", action="store_true", help="Disable debug logs")

parser.add_argument("--cache",    action="store_true", help="Use local HLTB cache")
parser.add_argument("--no-cache", action="store_true", help="Ignore and rebuild cache")

cli = parser.parse_args()

# ── effective values ────────────────────────────────────────────────────
export_csv = _tri_state(cli.csv,  cli.no_csv,  EXPORT_TO_CSV)
debug      = _tri_state(cli.debug, cli.no_debug, HLTB_DEBUG)
use_cache  = _tri_state(cli.cache, cli.no_cache, USE_CACHE)

analyse(
    steam_id      = STEAM_ID64,
    api_key       = STEAM_API_KEY,
    max_duration  = _int(cli.duration, MAX_DURATION),
    limit         = _int(cli.limit,    LIMIT),
    only_unplayed = cli.unplayed if cli.unplayed else FILTER_UNPLAYED,
    export_csv    = export_csv,
    debug         = debug,
    use_cache     = use_cache,
)

if __name__ == "__main__":
    # argparse already executed; nothing else needed
    pass
