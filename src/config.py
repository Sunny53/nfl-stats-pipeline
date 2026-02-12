"""
Configuration management for NFL Stats ETL Pipeline.
Loads environment variables and provides centralized settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load environment variables
load_dotenv()

# Project root directory
ROOT_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://localhost:5432/nfl_stats",
        env="DATABASE_URL",
        description="PostgreSQL connection string"
    )
    
    # API Configuration
    espn_api_base_url: str = Field(
        default="http://site.api.espn.com/apis/site/v2/sports/football/nfl",
        env="ESPN_API_BASE_URL"
    )
    
    weather_api_key: str = Field(
        default="",
        env="WEATHER_API_KEY",
        description="OpenWeatherMap API key (optional)"
    )
    
    # Pipeline Configuration
    current_season: int = Field(default=2024, env="CURRENT_SEASON")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: int = Field(default=5, env="RETRY_DELAY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/etl_pipeline.log", env="LOG_FILE")
    
    # Timezone
    timezone: str = Field(default="America/New_York", env="TIMEZONE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()


# ESPN API Endpoints
class ESPNEndpoints:
    """ESPN API endpoint templates."""
    
    BASE = settings.espn_api_base_url
    
    # Scoreboard (current week games)
    SCOREBOARD = f"{BASE}/scoreboard"
    
    # Teams
    TEAMS = f"{BASE}/teams"
    TEAM_DETAIL = f"{BASE}/teams/{{team_id}}"
    TEAM_ROSTER = f"{BASE}/teams/{{team_id}}/roster"
    
    # Standings
    STANDINGS = f"{BASE}/standings"
    
    # Schedule
    SCHEDULE = f"{BASE}/teams/{{team_id}}/schedule"
    
    # Player Stats
    PLAYER_STATS = f"{BASE}/athletes/{{player_id}}/statistics"


# Database Schema Names
class DatabaseSchemas:
    """Database schema organization."""
    
    RAW = "raw_data"          # Untransformed API responses
    PROCESSED = "processed"   # Cleaned and validated data
    ANALYTICS = "analytics"   # Calculated metrics and aggregations


# Metric Calculation Constants
class MetricConstants:
    """Constants for metric calculations."""
    
    # Clutch Performance Index
    CLUTCH_SCORE_MARGIN = 7  # Points within which game is considered close
    CLUTCH_QUARTER = 4       # Quarter for clutch situations
    
    # Snap Efficiency
    MIN_SNAPS_THRESHOLD = 10  # Minimum snaps to qualify for efficiency rating
    
    # Consistency Score
    MIN_GAMES_FOR_CONSISTENCY = 4  # Minimum games to calculate consistency
    
    # Fatigue Factor
    SHORT_REST_DAYS = 6      # Games with < 6 days rest are fatigued
    LONG_TRAVEL_MILES = 1500 # Coast-to-coast threshold
    
    # Momentum Shift
    MOMENTUM_WEIGHTS = {
        'turnover_to_score': 3.0,
        'goal_line_stand': 2.5,
        'fourth_down_conversion': 2.0,
        'big_play_after_score': 1.5,
    }


# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': settings.log_level,
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': settings.log_level,
            'formatter': 'json',
            'filename': settings.log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'root': {
        'level': settings.log_level,
        'handlers': ['console', 'file']
    }
}


# NFL Team Mapping (for reference)
NFL_TEAMS = {
    'ARI': 'Arizona Cardinals',
    'ATL': 'Atlanta Falcons',
    'BAL': 'Baltimore Ravens',
    'BUF': 'Buffalo Bills',
    'CAR': 'Carolina Panthers',
    'CHI': 'Chicago Bears',
    'CIN': 'Cincinnati Bengals',
    'CLE': 'Cleveland Browns',
    'DAL': 'Dallas Cowboys',
    'DEN': 'Denver Broncos',
    'DET': 'Detroit Lions',
    'GB': 'Green Bay Packers',
    'HOU': 'Houston Texans',
    'IND': 'Indianapolis Colts',
    'JAX': 'Jacksonville Jaguars',
    'KC': 'Kansas City Chiefs',
    'LAC': 'Los Angeles Chargers',
    'LAR': 'Los Angeles Rams',
    'LV': 'Las Vegas Raiders',
    'MIA': 'Miami Dolphins',
    'MIN': 'Minnesota Vikings',
    'NE': 'New England Patriots',
    'NO': 'New Orleans Saints',
    'NYG': 'New York Giants',
    'NYJ': 'New York Jets',
    'PHI': 'Philadelphia Eagles',
    'PIT': 'Pittsburgh Steelers',
    'SEA': 'Seattle Seahawks',
    'SF': 'San Francisco 49ers',
    'TB': 'Tampa Bay Buccaneers',
    'TEN': 'Tennessee Titans',
    'WAS': 'Washington Commanders',
}


if __name__ == "__main__":
    # Test configuration loading
    print("Configuration loaded successfully!")
    print(f"Database URL: {settings.database_url[:30]}...")
    print(f"Current Season: {settings.current_season}")
    print(f"Log Level: {settings.log_level}")
    print(f"ESPN API Base: {ESPNEndpoints.BASE}")
