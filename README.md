# Steam Game Duration Toolkit 🎮⏱️

CLI tool that scans your Steam library and tells you which games …

- you still haven’t played (optional)  
- can be finished in **≤ _​X_​** hours, using data from [HowLongToBeat](https://howlongtobeat.com)

It keeps a local JSON cache so repeat runs are instant.

---

## 🔧 Setup

```bash
git clone https://github.com/your‑user/steam‑toolkit.git
cd steam‑toolkit
cp .env.example .env         # add your Steam key + ID64
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Usage

Run with defaults from `.env`:

```bash
python run.py
```

Full‑library scan (no limit):

```bash
python run.py --duration 5 --limit 0
```

Custom example:

```bash
python run.py --duration 4 --limit 20 --no-csv --all --debug --no-cache
```

---

### CLI flags

| Flag                     | Description                                           |
|--------------------------|-------------------------------------------------------|
| `--duration N`           | Max main‑story hours                                  |
| `--limit N`              | Max games to process (`0` = all)                      |
| `--csv` / `--no-csv`     | Enable / disable CSV export                           |
| `--unplayed`             | Only games with 0 minutes played                      |
| `--debug` / `--no-debug` | Enable / disable HLTB debug output                    |
| `--cache` / `--no-cache` | Force use / ignore `hltb_cache.json`                  |


---

## ⚙️ Configuration (`.env`)

```dotenv
# Steam
STEAM_API_KEY=
STEAM_ID64=

# Filters
MAX_DURATION=5          # hours
LIMIT=0                 # 0 = no limit
FILTER_UNPLAYED=true    # true / false

# Output
EXPORT_TO_CSV=true      # true / false

# Debug
HLTB_DEBUG=false        # true logs HLTB matches

# Cache
USE_CACHE=true          # false == behave like --no-cache
```

> Do **not** commit your `.env`. Keep `.env.example` in the repo.

---

## 📦 Output

Printed list + optional CSV (`filtered_games.csv`):

```
Searching games with main story ≤ 5 h …

VVVVVV [LIVE]
  • Main : 2.41 h
  • Extra: 3.45 h
  • 100% : 4.93 h
```

---

## 🗄️ Cache

- File: **`hltb_cache.json`** (root folder)  
- Delete it anytime or run with `--no-cache` (or `USE_CACHE=false`) to refresh.  
- First full‑run populates the cache; later runs are instant.

---

## 📁 Project layout

```
steam_toolkit/
│  combine.py
│  config.py
│  filters.py
│  hltb_api.py
│  hltb_cache.py
│  steam_api.py
run.py
.env.example
requirements.txt
README.md
.gitignore
```

---

## 🧑‍💻 License

[MIT](LICENSE) — use it, fork it, improve it.
