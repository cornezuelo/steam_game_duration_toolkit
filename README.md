# Steam Game Duration Toolkit 🎮⏱️

CLI utility that scans your Steam library, fetches play‑time estimates from [HowLongToBeat](https://howlongtobeat.com) and tells you which games fit your schedule.

- Optional filter: **only unplayed titles**
- Configurable main‑story limit (≤ N hours)
- Fuzzy multi‑pass matching with a local JSON cache
- Per‑title overrides for edge‑cases
- Exports two CSVs: **matched** and **unmatched**

---

## 🔧 Setup

```bash
git clone https://github.com/your‑user/steam‑toolkit.git
cd steam‑toolkit
cp .env.example .env       # add your Steam key + ID64
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Quick start

```bash
# defaults from .env
python run.py
```

Full library, 5 h ceiling:

```bash
python run.py --duration 5 --limit 0
```

Live look‑ups, no cache, debug on, stricter similarity:

```bash
python run.py --duration 4 --debug --no-cache --sim 0.80
```

---

### CLI flags

| Flag / env               | Description                                      |
| ------------------------ | ------------------------------------------------ |
| `--duration N`           | Max main‑story hours                             |
| `--limit N`              | Max games to process (`0` = all)                 |
| `--csv` / `--no-csv`     | Enable / disable CSV export                      |
| `--unplayed`             | Only games with 0 minutes played                 |
| `--all`                  | Include played games (overrides `--unplayed`)    |
| `--debug` / `--no-debug` | Show / hide HLTB debug output                    |
| `--cache` / `--no-cache` | Force use / ignore `hltb_cache.json`             |
| `--sim X`                | Min similarity (0‑1). Overrides `MIN_SIMILARITY` |

---

## ⚙️ Configuration (`.env`)

```dotenv
# Steam credentials
STEAM_API_KEY=
STEAM_ID64=

# Filters
MAX_DURATION=5
LIMIT=0
FILTER_UNPLAYED=true     # default when no --unplayed / --all

# Output
EXPORT_TO_CSV=true

# Cache & debug
USE_CACHE=true
HLTB_DEBUG=false

# Matching
MIN_SIMILARITY=0.75      # default threshold (0‑1)
OVERRIDES_PATH=overrides.json
```

---

## 📦 Outputs

| File                  | When created                 | Contents                 |
| --------------------- | ---------------------------- | ------------------------ |
| `filtered_games.csv`  | `--csv` and ≥ 1 match        | Titles within time limit |
| `unmatched_games.csv` | `--csv` and ≥ 1 mismatch     | Games with no HLTB hit   |
| `hltb_cache.json`     | always (unless `--no-cache`) | Durations cache          |

Terminal example:

```
Searching games with main story ≤ 3 h …

VVVVVV [LIVE]
  • Main : 2.4 h
```

---

## 🗂️ Overrides (`overrides.json`)

```json
{
  "Odd Steam Title": "Exact HLTB Query",
  "Broken Demo Name": null               // skip this entry entirely
}
```

Overrides are checked **before** any normalisation passes.

---

## 🗄️ Project layout

```
steam_toolkit/
│  combine.py        # core analysis
│  config.py         # .env loader
│  filters.py
│  hltb_api.py       # multipass matcher
│  hltb_cache.py
│  steam_api.py
run.py               # CLI launcher
overrides.json       # optional
hltb_cache.json      # generated
.env.example
requirements.txt
README.md
```

---

## 🧑‍💻 License

[MIT](LICENSE) — fork it, improve it, enjoy it.

