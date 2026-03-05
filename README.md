# NFL Clutch Analytics Dashboard

A data pipeline and analytics dashboard for NFL quarterback and wide receiver performance metrics.

🔗 **[Live Dashboard](https://nfl-stats-pipeline.streamlit.app/)**

---

## What It Does

This project pulls weekly NFL player data from 2015 to present, aggregates it into seasonal stats, calculates advanced efficiency metrics, and displays them in an interactive Streamlit dashboard.

**Positions covered:** QB, WR  
**Seasons:** 2015 → current  
**Data source:** [nfl_data_py](https://github.com/nflverse/nfl_data_py)  
**Database:** Supabase (PostgreSQL)

---

## Metrics

### Snap Efficiency
Measures how many yards a player produces per offensive snap.

- **QB:** `passing_yards / total_snaps`
- **WR:** `receiving_yards / total_snaps`

Higher is better. Uses real snap counts from NFL play-by-play data.

---

### Consistency Score
Measures how reliably a player performs week to week. Based on the Coefficient of Variation (CV) of weekly yards.

```
CV = std_dev(weekly_yards) / mean(weekly_yards)
consistency_score = max(0, 100 - (CV × 100))
```

- Score of **100** = perfectly consistent (unrealistic)
- Score of **70+** = very consistent producer
- Score of **40-60** = boom/bust player
- Score of **0** = extremely volatile

---

## Qualifying Thresholds

Only qualified players appear in leaderboards:

| Position | Threshold |
|----------|-----------|
| QB | 200+ pass attempts |
| WR | 40+ targets |

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Data extraction | nfl_data_py |
| Transformation | Python / pandas |
| Database | Supabase (PostgreSQL) |
| Dashboard | Streamlit |
| Hosting | Streamlit Cloud |
| Docs | GitHub Pages |

---

## Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/Sunny53/nfl-stats-pipeline.git
cd nfl-stats-pipeline
```

**2. Create and activate virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add environment variables**

Create a `.env` file in the project root:
```
SUPABASE_DB_URL=your_supabase_connection_string
```

**5. Run the ETL pipeline**
```bash
python -m etl.pipeline
```

**6. Launch the dashboard**
```bash
python -m streamlit run streamlit_app/app.py
```

---

## Project Structure

```
nfl-stats-pipeline/
├── etl/
│   ├── extract.py       # Downloads NFL data
│   ├── transform.py     # Aggregates weekly → seasonal, calculates metrics
│   ├── load.py          # Writes to Supabase
│   └── pipeline.py      # Orchestrates ETL
├── streamlit_app/
│   ├── app.py           # Main dashboard
│   └── utils/db.py      # Database queries
├── database/
│   ├── schema.sql       # Table definitions
│   └── views.sql        # Leaderboard views
├── docs/                # GitHub Pages
└── requirements.txt
```

---

## Roadmap

- [ ] Clutch Performance Index
- [ ] Value Per Dollar (player production relative to salary via OverTheCap)
- [ ] Fatigue Factor (short rest, travel distance, weather conditions)
- [ ] Momentum Shifts (big play analysis)
- [ ] Migrate data source from nfl_data_py to RapidAPI for real-time updates
- [ ] Microsoft Power BI embedded dashboards for advanced visual analytics
- [ ] 2025 season data (auto-updates when available)

---

*Built by [Sunny53](https://github.com/Sunny53)*
