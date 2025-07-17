"""
steam_toolkit.hltb_api
----------------------

Resolve a Steam title into HowLongToBeat durations.

Order of attempts
1. Override  (overrides.json: "Steam Title" → "Custom HLTB Query")
2. Exact Steam title
3. Normalised title – three increasingly aggressive passes

A match is accepted as soon as `similarity >= min_similarity`
(default pulled from config.MIN_SIMILARITY).

Set `debug=True` (CLI flag --debug) to print every step.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import re, json
from howlongtobeatpy import HowLongToBeat
from steam_toolkit.config import (
    HLTB_DEBUG,
    HLTB_MIN_SIMILARITY,
    HLTB_OVERRIDES_PATH,
)

# ── Data container ─────────────────────────────────────────────────────
@dataclass
class GameDuration:
    name: str
    main_story: Optional[float]
    main_extra: Optional[float]
    completionist: Optional[float]


# ── Overrides ──────────────────────────────────────────────────────────
def _load_overrides(path: Path) -> Dict[str, str | None]:
    if not path.exists():
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_OVERRIDES = _load_overrides(Path(HLTB_OVERRIDES_PATH))


# ── Regex arsenal ──────────────────────────────────────────────────────
_amp    = re.compile(r"[&:]")            # symbols we simply drop
_paren  = re.compile(r"\(.*?\)")         # text inside parentheses
_tail   = re.compile(r"[™®].*$|[–\-|]\s.*$")   # dash / pipe / ™ / ® suffix
_year   = re.compile(r"\b(19|20)\d{2}\b")      # standalone year
_noise  = re.compile(                      # commercial fluff
    r"\b(single ?player|multiplayer|demo|beta|alpha|test|edition|enhanced|"
    r"definitive|director'?s cut|ultimate|complete|goty|remaster|collection|"
    r"dlc|episode|mod|remake)\b",
    flags=re.I,
)
_dotted = re.compile(r"\b(?:[A-Z]\.){2,}")     # S.T.A.L.K.E.R. → STALKER
_num1   = re.compile(r"\s+\d\b")               # trailing single digit


# ── Normalisation passes (increasingly aggressive) ─────────────────────
def _pass1(title: str) -> str:
    """
    Pass 1  – "light trim"
        · remove symbols  (& :)
        · strip parentheses
        · cut suffix after first dash / ™ / ®
    """
    t = _amp.sub(" ", title)
    t = _paren.sub("", t)
    t = _tail.sub("", t)
    return " ".join(t.split()).strip()


def _pass2(title: str) -> str:
    """
    Pass 2  – "remove fluff"
        · everything from pass 1
        · drop standalone years 1990‑2099
        · remove noisy marketing words (demo, GOTY, Definitive…)
    """
    t = _pass1(title)
    t = _year.sub("", t)
    t = _noise.sub("", t)
    return " ".join(t.split()).strip()


def _pass3(title: str) -> str:
    """
    Pass 3  – "aggressive"
        · everything from pass 2
        · collapse dotted acronyms  (S.T.A.L.K.E.R. → STALKER)
        · remove trailing single digit  ("Wasteland 1" → "Wasteland")
        · Title‑case if the whole string is FULLCAPS
    """
    t = _pass2(title)
    t = _dotted.sub(lambda m: m.group(0).replace(".", ""), t)
    t = _num1.sub("", t)
    t = " ".join(t.split())
    return t.title() if t.isupper() else t

# ── Debug helpers ──────────────────────────────────────────────────────
_sep = "─" * 72

def _dump(header: str, rows: List, dbg: bool):
    if not dbg:
        return
    print(f"\n{_sep}\n{header}")
    for r in rows[:5]:
        main = f"{r.main_story:.2f} h" if r.main_story else "—"
        print(f"  • {r.game_name:<55} main={main:<7} sim={r.similarity:.2f}")


# ── Single HLTB query ─────────────────────────────────────────────────
def _query(q: str, dbg: bool) -> Optional[Tuple[GameDuration, float]]:
    res = HowLongToBeat().search(q)
    if not res:
        _dump(f"[HLTB] No results: {q}", [], dbg)
        return None
    res.sort(key=lambda r: r.similarity, reverse=True)
    _dump(f"[HLTB] Query: {q}", res, dbg)
    best = res[0]
    return GameDuration(best.game_name, best.main_story, best.main_extra, best.completionist), best.similarity


# ── Public function ───────────────────────────────────────────────────
def search_game_duration(
    steam_title: str,
    *,
    debug: bool = HLTB_DEBUG,
    min_similarity: float = HLTB_MIN_SIMILARITY,
) -> Optional[GameDuration]:
    """
    Return GameDuration if best match ≥ min_similarity, else None.
    Debug output obeys `debug` param.
    """

    # 0) override
    if steam_title in _OVERRIDES:
        target = _OVERRIDES[steam_title]
        if target is None:                       # explicit skip
            _dump(f"[HLTB] override → skip: {steam_title}", [], debug)
            return None
        _dump(f"[HLTB] override: {steam_title} → {target}", [], debug)
        res = _query(target, debug)
        if res and res[1] >= min_similarity:
            return res[0]

    # 1) exact title
    res = _query(steam_title, debug)
    if res and res[1] >= min_similarity:
        return res[0]

    # 2‑4) progressively aggressive passes
    for i, normaliser in enumerate((_pass1, _pass2, _pass3), start=1):
        norm = normaliser(steam_title)
        if norm == steam_title:
            continue
        _dump(f"[HLTB] → pass{i}: {norm}", [], debug)
        res = _query(norm, debug)
        if res and res[1] >= min_similarity:
            return res[0]

    _dump(f"[HLTB] Unmatched: {steam_title}", [], debug)
    return None
