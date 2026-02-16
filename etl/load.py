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

def insert_players(df):
    """Insert players into dim_players."""
    engine = get_engine()
    
    # Clear existing
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE dim_players CASCADE"))
        conn.commit()
    
    # Insert
    df.to_sql('dim_players', engine, if_exists='append', index=False)
    print(f"Inserted {len(df)} players")

def insert_seasons(df):
    """Insert season stats into fact_player_seasons."""
    engine = get_engine()
    
    # Truncate table first
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE fact_player_seasons"))
        conn.commit()
        print("Truncated fact_player_seasons")
    
    # Define explicit column types for to_sql
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
    
    df.to_sql('fact_player_seasons', engine, if_exists='append', index=False, dtype=dtype)
    print(f"Inserted {len(df)} season records")

def test_connection():
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
    test_connection()