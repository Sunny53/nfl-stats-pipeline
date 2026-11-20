import os
from sqlalchemy import create_engine, text
from pathlib import Path
import pandas as pd
from sqlalchemy.types import Integer, Numeric, String

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
ENV_PATH = PROJECT_ROOT / '.env'

def load_env():
    """Read .env file manually."""
    env = {}
    try:
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()
        return env
    except Exception as e:
        print(f"Warning: Could not load .env: {e}")
        return {}

def get_engine():
    """Create database engine from environment."""
    env = load_env()
    db_url = env.get('SUPABASE_DB_URL')
    
    if not db_url:
        raise ValueError("SUPABASE_DB_URL not found in .env")
    
    return create_engine(db_url, pool_pre_ping=True)

def insert_players(conn, df):
    """Insert players using the caller's transaction."""
    df.to_sql('dim_players', conn, if_exists='append', index=False)


def insert_seasons(conn, df):
    """Insert season stats using the caller's transaction."""
    dtype = {
        'player_id': String,
        'season_year': Integer,
        'team': String,
        'games': Integer,
        'snaps': Integer,
        'attempts': Integer,
        'completions': Integer,
        'yards': Integer,
        'tds': Integer,
        'ints': Integer,
        'snap_efficiency': Numeric(10, 4),
        'yards_per_attempt': Numeric(10, 2),
        'weekly_cv': Numeric(10, 4),
        'consistency_score': Numeric(10, 2)
    }
    df.to_sql(
        'fact_player_seasons', conn, if_exists='append', index=False, dtype=dtype
    )


def load_data(players_df, seasons_df):
    """Replace both tables atomically."""
    engine = get_engine()
    with engine.begin() as conn:
        if conn.dialect.name == "sqlite":
            conn.execute(text("DELETE FROM fact_player_seasons"))
            conn.execute(text("DELETE FROM dim_players"))
        else:
            conn.execute(text("TRUNCATE TABLE dim_players CASCADE"))
        insert_players(conn, players_df)
        insert_seasons(conn, seasons_df)

    print(f"Inserted {len(players_df)} players")
    print(f"Inserted {len(seasons_df)} season records")


def check_connection():
    """Test database connectivity."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected: {version[:60]}...")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    check_connection()