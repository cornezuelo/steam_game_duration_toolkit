"""
Load all configuration values from .env
"""

import os
from dotenv import load_dotenv

load_dotenv()

def _to_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "yes")

# Steam
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_ID64    = os.getenv("STEAM_ID64")

# Filters
MAX_DURATION    = int(os.getenv("MAX_DURATION", 5))
LIMIT           = int(os.getenv("LIMIT", 0))
FILTER_UNPLAYED = _to_bool(os.getenv("FILTER_UNPLAYED", "true"))

# Output
EXPORT_TO_CSV = _to_bool(os.getenv("EXPORT_TO_CSV", "true"))

# Debug / cache
HLTB_DEBUG = _to_bool(os.getenv("HLTB_DEBUG", "false"))
USE_CACHE  = _to_bool(os.getenv("USE_CACHE", "true"))
