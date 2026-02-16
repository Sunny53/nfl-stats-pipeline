# NFL Stats Pipeline

Interactive analytics platform for NFL quarterback and wide receiver performance metrics.

## Tech Stack

- **Data Source**: nfl-data-py (Python)
- **ETL**: Python + Pandas
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Streamlit
- **Hosting**: Streamlit Cloud (free tier)

## Metrics

### Snap Efficiency
Yards per estimated snap. Higher = more productive per opportunity.

**Formula**: `yards / (games × 60 for QB, games × 50 for WR)`

### Consistency Score
Placeholder - calculated from weekly performance variance (0-100 scale).

## Data Pipeline

```bash
# Run ETL pipeline
python -m etl.pipeline