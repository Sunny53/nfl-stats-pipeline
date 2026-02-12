# 🏈 NFL Stats ETL Pipeline & Analytics Dashboard

## 📊 Project Overview

An automated data pipeline that transforms raw NFL statistics into actionable insights through unique performance metrics. This project showcases end-to-end data engineering capabilities including extraction, transformation, storage, automation, and visualization.

### 🎯 What Makes This Different

Instead of displaying standard box scores, this pipeline calculates:

**💰 Value Metrics:**
- **Points Per Dollar (PPD)**: Player ROI based on salary cap efficiency
- **Snap Efficiency Rating**: Production per opportunity (normalized for playing time)
- **Consistency Score**: Week-to-week reliability using variance analysis

**🎯 Situational Performance:**
- **Clutch Performance Index**: How players perform under pressure vs. normal situations
- **Momentum Shift Score**: Quantifying game-changing plays and swing events
- **Fatigue Factor Index**: Performance impact of schedule density and travel

## 🏗️ Architecture

```
┌──────────────────┐
│  ESPN API        │
│  Salary Data     │──────┐
│  Weather API     │      │
└──────────────────┘      │
                          ▼
                   ┌─────────────────┐
                   │  Python ETL     │
                   │  - Extract      │
                   │  - Transform    │
                   │  - Calculate    │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  PostgreSQL     │
                   │  (Supabase)     │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  GitHub Actions │
                   │  (Daily 6AM ET) │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Power BI       │
                   │  Dashboard      │
                   └─────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Extraction** | Python 3.11, Requests | API integration, data fetching |
| **Transformation** | Pandas, NumPy | Data cleaning, metric calculation |
| **Storage** | PostgreSQL 15, SQLAlchemy | Normalized relational database |
| **Orchestration** | GitHub Actions | Automated daily pipeline execution |
| **Visualization** | Power BI Desktop | Interactive dashboards |
| **Hosting** | Supabase (DB), GitHub, Power BI Service | Cloud infrastructure |

## 📁 Project Structure

```
nfl-stats-pipeline/
│
├── .github/
│   └── workflows/
│       └── etl_pipeline.yml          # Automation workflow
│
├── src/
│   ├── config.py                     # Configuration management
│   ├── database/
│   │   ├── connection.py             # Database connection pooling
│   │   ├── models.py                 # SQLAlchemy ORM models
│   │   └── schema.sql                # Database schema DDL
│   │
│   ├── extraction/
│   │   ├── api_client.py             # ESPN API wrapper
│   │   ├── extractors.py             # Data fetching orchestration
│   │   └── salary_scraper.py         # Salary cap data collection
│   │
│   ├── transformation/
│   │   ├── cleaners.py               # Data cleaning & validation
│   │   ├── value_metrics.py          # PPD, Snap Efficiency, Consistency
│   │   └── situational_metrics.py    # Clutch, Momentum, Fatigue
│   │
│   └── utils/
│       ├── logger.py                 # Structured logging
│       └── helpers.py                # Utility functions
│
├── scripts/
│   ├── run_etl.py                    # Main ETL orchestrator
│   ├── setup_db.py                   # Database initialization
│   └── backfill_historical.py        # Historical data loader
│
├── tests/
│   ├── test_extraction.py
│   ├── test_transformation.py
│   └── test_metrics.py
│
├── dashboards/
│   └── nfl_analytics.pbix            # Power BI dashboard file
│
├── notebooks/
│   └── metric_validation.ipynb       # Metric testing & validation
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or Supabase account)
- Power BI Desktop
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/nfl-stats-pipeline.git
cd nfl-stats-pipeline
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Initialize database**
```bash
python scripts/setup_db.py
```

6. **Run initial ETL**
```bash
python scripts/run_etl.py
```

## 📊 Sample Insights

*[Will be populated after dashboard creation]*

- **Most Undervalued Player**: [Player Name] with PPD of X (producing elite stats at rookie contract)
- **Clutch King**: [Player Name] performs 35% better in high-pressure situations
- **Consistency Leader**: [Team Name] has lowest variance in weekly performance (ideal playoff team)

## 🔄 Automation

The pipeline runs automatically:
- **Schedule**: Daily at 6:00 AM EST
- **Trigger**: GitHub Actions workflow
- **Duration**: ~5-8 minutes per run
- **Notifications**: Errors logged to GitHub Actions

Manual trigger available via GitHub Actions UI.

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_metrics.py -v

# Check code coverage
pytest --cov=src tests/
```

## 📈 Unique Metrics Explained

### Value Metrics 💰

**Points Per Dollar (PPD)**
```
PPD = Player's Expected Points Added (EPA) / Annual Salary (in millions)
```
Identifies undervalued players who maximize production relative to cost.

**Snap Efficiency Rating**
```
Snap Efficiency = (Total Production Score) / (% of Team Snaps Played)
```
Reveals high-impact players with limited opportunities.

**Consistency Score**
```
Consistency = 100 - (Coefficient of Variation × 100)
CV = (Std Dev / Mean) × 100
```
Measures week-to-week reliability (critical for playoffs).

### Situational Metrics 🎯

**Clutch Performance Index (CPI)**
```
CPI = (Success Rate in Clutch Situations / Overall Success Rate) × 100
```
Clutch = 4th quarter, within 7 points, or critical 3rd/4th downs.

**Momentum Shift Score**
Weighted sum of swing events (turnovers, goal-line stands, 4th down conversions).

**Fatigue Factor Index**
Performance degradation based on rest days, travel distance, and injury load.

## 🔮 Future Enhancements

- [ ] Schedule-Adjusted Performance (normalize for opponent strength)
- [ ] Machine learning predictions for playoff outcomes
- [ ] Real-time streaming data integration
- [ ] REST API for external consumption
- [ ] Sentiment analysis from social media

## 📝 Data Sources

- **Game Stats**: ESPN API (unofficial endpoints)
- **Historical Data**: nfl-data-py library
- **Salary Data**: OverTheCap.com / Spotrac
- **Weather Data**: OpenWeatherMap API

## 🎓 What I Learned

- Building production-grade ETL pipelines with error handling
- Designing normalized database schemas for analytics
- Implementing custom statistical metrics from domain research
- Orchestrating automated workflows with GitHub Actions
- Creating business-focused dashboards that tell stories

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Connect

**[Your Name]**
- LinkedIn: [Your LinkedIn]
- Email: [Your Email]
- Portfolio: [Your Website]

---

*This project demonstrates end-to-end data engineering skills including API integration, data transformation, database design, automation, and business intelligence visualization.*
