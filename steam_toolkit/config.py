"""
Centralised .env loader.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _bool(v: str) -> bool:
    return v.strip().lower() in ("true", "1", "yes")

# ── Steam credentials ──────────────────────────────────────────────────
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_ID64    = os.getenv("STEAM_ID64")

# ── Library filters ────────────────────────────────────────────────────
MAX_DURATION    = int(os.getenv("MAX_DURATION", 5))
LIMIT           = int(os.getenv("LIMIT", 0))
FILTER_UNPLAYED = _bool(os.getenv("FILTER_UNPLAYED", "true"))

# ── Output options ─────────────────────────────────────────────────────
EXPORT_TO_CSV = _bool(os.getenv("EXPORT_TO_CSV", "true"))

# ── Runtime toggles ────────────────────────────────────────────────────
USE_CACHE  = _bool(os.getenv("USE_CACHE",  "true"))
HLTB_DEBUG = _bool(os.getenv("HLTB_DEBUG", "false"))

# ── Matching threshold (NEW) ───────────────────────────────────────────
HLTB_MIN_SIMILARITY = float(os.getenv("MIN_SIMILARITY", 0.75))          # ◆

# ── Overrides path  (NEW) ──────────────────────────────────────────────
HLTB_OVERRIDES_PATH = Path(os.getenv("OVERRIDES_PATH", "overrides.json"))  # ◆
