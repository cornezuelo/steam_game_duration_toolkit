"""
steam_toolkit.hltb_api
----------------------

Utility that, given a Steam game title, returns its durations from
HowLongToBeat (main‑story / main+extra / completionist).

Lookup order
1. Exact Steam title.
2. Normalised title (symbols & : removed, noise words stripped, etc.).

Set `debug=True` (or pass `--debug` in the CLI) to see detailed match blocks.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, List
import re
from howlongtobeatpy import HowLongToBeat


# ── result container ────────────────────────────────────────────────────
@dataclass
class GameDuration:
    name: str
    main_story: Optional[float]
    main_extra: Optional[float]
    completionist: Optional[float]


# ── regexes for cleaning ────────────────────────────────────────────────
_symbols = re.compile(r"[&:]", flags=re.I)           # drop & and :
_paren   = re.compile(r"\(.*?\)")                    # remove "(…)"
_tail    = re.compile(r"[™®].*$|[–\-|]\s.*$")        # cut dash / ™ / ® suffix
_year    = re.compile(r"\b(19|20)\d{2}\b")           # strip standalone year
_noise   = re.compile(
    r"\b("
    r"single ?player|multiplayer|demo|beta|alpha|test|edition|enhanced|definitive|"
    r"director'?s cut|ultimate|complete|goty|remaster|collection|dlc|episode|mod|remake"
    r")\b",
    flags=re.I,
)
_dotted  = re.compile(r"\b(?:[A-Z]\.){2,}")          # S.T.A.L.K.E.R. → STALKER
_num1    = re.compile(r"\b\d{1}\b$")                 # trailing “ 1”


def _normalise(title: str) -> str:
    """Return a cleaned‑up version of the Steam title for HLTB lookup."""
    t = _symbols.sub(" ", title)
    t = _paren.sub("", t)
    t = _tail.sub("", t)
    t = _year.sub("", t)
    t = _noise.sub("", t)
    t = _dotted.sub(lambda m: m.group(0).replace(".", ""), t)
    t = _num1.sub("", t)
    t = " ".join(t.split()).strip()
    return t.title() if t.isupper() else t


# ── debug printer ───────────────────────────────────────────────────────
_sep = "─" * 72


def _dump(header: str, rows: List, dbg: bool) -> None:
    if not dbg:
        return
    print(f"\n{_sep}\n{header}")
    for r in rows[:5]:
        main = f"{r.main_story:.2f} h" if r.main_story else "—"
        print(f"  • {r.game_name:<55} main={main:<8} sim={r.similarity:.2f}")


# ── internal search helper ──────────────────────────────────────────────
def _search(query: str, dbg: bool) -> Optional[Tuple[GameDuration, float]]:
    res = HowLongToBeat().search(query)
    if not res:
        _dump(f"[HLTB] No results for: {query}", [], dbg)
        return None
    res.sort(key=lambda r: r.similarity, reverse=True)
    _dump(f"[HLTB] Query: {query}", res, dbg)
    best = res[0]
    return (
        GameDuration(best.game_name, best.main_story, best.main_extra, best.completionist),
        best.similarity,
    )


# ── public API ──────────────────────────────────────────────────────────
def search_game_duration(
    steam_title: str,
    debug: bool = False,
    min_similarity: float = 0.75,
) -> Optional[GameDuration]:
    """Return GameDuration if best match ≥ min_similarity, else None."""
    # 1) exact title
    res = _search(steam_title, debug)
    if res and res[1] >= min_similarity:
        return res[0]

    # 2) normalised title
    norm = _normalise(steam_title)
    if norm != steam_title:
        _dump(f"[HLTB] -> retry (normalised): {norm}", [], debug)
        res = _search(norm, debug)
        if res and res[1] >= min_similarity:
            return res[0]

    _dump(f"[HLTB] No reliable match for: {steam_title}", [], debug)
    return None
