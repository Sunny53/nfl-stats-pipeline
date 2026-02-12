"""
Helper utility functions for data processing and transformations.
"""

import re
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import pytz


def safe_get(data: Dict, *keys, default=None) -> Any:
    """
    Safely navigate nested dictionaries.
    
    Args:
        data: Dictionary to navigate
        *keys: Sequence of keys to traverse
        default: Default value if key path doesn't exist
    
    Returns:
        Value at key path or default
    
    Example:
        safe_get(game, 'competitions', 0, 'competitors', 0, 'team', 'displayName')
    """
    try:
        result = data
        for key in keys:
            if isinstance(result, list):
                result = result[int(key)]
            else:
                result = result[key]
        return result if result is not None else default
    except (KeyError, IndexError, TypeError, ValueError):
        return default


def parse_espn_datetime(date_str: str, tz_str: str = 'America/New_York') -> Optional[datetime]:
    """
    Parse ESPN API datetime string to timezone-aware datetime.
    
    Args:
        date_str: ISO format datetime string
        tz_str: Timezone string (default: America/New_York)
    
    Returns:
        Timezone-aware datetime object or None if parsing fails
    """
    try:
        # Parse ISO format
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        # Convert to specified timezone
        tz = pytz.timezone(tz_str)
        return dt.astimezone(tz)
    except (ValueError, AttributeError) as e:
        return None


def clean_team_name(name: str) -> str:
    """
    Standardize team name format.
    
    Args:
        name: Raw team name
    
    Returns:
        Cleaned team name
    """
    if not name:
        return ""
    
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name.strip())
    
    return name


def extract_team_abbreviation(team_data: Dict) -> str:
    """
    Extract team abbreviation from ESPN team data.
    
    Args:
        team_data: ESPN team object
    
    Returns:
        Team abbreviation (e.g., 'KC', 'SF')
    """
    return safe_get(team_data, 'abbreviation', default='UNK')


def extract_player_position(athlete_data: Dict) -> str:
    """
    Extract player position from ESPN athlete data.
    
    Args:
        athlete_data: ESPN athlete object
    
    Returns:
        Position abbreviation (e.g., 'QB', 'RB', 'WR')
    """
    return safe_get(athlete_data, 'position', 'abbreviation', default='UNK')


def calculate_time_difference(start: datetime, end: datetime) -> float:
    """
    Calculate time difference in seconds.
    
    Args:
        start: Start datetime
        end: End datetime
    
    Returns:
        Difference in seconds
    """
    return (end - start).total_seconds()


def convert_yards_to_meters(yards: float) -> float:
    """
    Convert yards to meters.
    
    Args:
        yards: Distance in yards
    
    Returns:
        Distance in meters
    """
    return yards * 0.9144


def is_home_game(competitor: Dict, team_id: str) -> bool:
    """
    Determine if team is playing at home.
    
    Args:
        competitor: ESPN competitor object
        team_id: Team ID to check
    
    Returns:
        True if home game, False otherwise
    """
    comp_team_id = safe_get(competitor, 'team', 'id')
    home_away = safe_get(competitor, 'homeAway')
    
    return comp_team_id == team_id and home_away == 'home'


def extract_score(competitor: Dict) -> int:
    """
    Extract score from competitor data.
    
    Args:
        competitor: ESPN competitor object
    
    Returns:
        Score as integer (0 if not available)
    """
    score = safe_get(competitor, 'score', default='0')
    
    try:
        return int(score)
    except (ValueError, TypeError):
        return 0


def is_game_final(game_status: Dict) -> bool:
    """
    Check if game has finished.
    
    Args:
        game_status: ESPN game status object
    
    Returns:
        True if game is final, False otherwise
    """
    status_type = safe_get(game_status, 'type', 'name', default='').lower()
    return 'final' in status_type or 'complete' in status_type


def get_week_number(date: datetime, season_start: datetime) -> int:
    """
    Calculate NFL week number from date.
    
    Args:
        date: Game date
        season_start: Season start date
    
    Returns:
        Week number (1-18)
    """
    days_diff = (date - season_start).days
    week = (days_diff // 7) + 1
    
    return max(1, min(week, 18))  # Clamp to 1-18


def format_money(amount: float) -> str:
    """
    Format dollar amount for display.
    
    Args:
        amount: Dollar amount
    
    Returns:
        Formatted string (e.g., "$15.2M")
    """
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.1f}K"
    else:
        return f"${amount:.0f}"


def calculate_percentage(numerator: float, denominator: float, decimals: int = 1) -> float:
    """
    Calculate percentage with safe division.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        decimals: Decimal places to round
    
    Returns:
        Percentage value (0.0 if denominator is 0)
    """
    if denominator == 0:
        return 0.0
    
    percentage = (numerator / denominator) * 100
    return round(percentage, decimals)


def normalize_player_name(name: str) -> str:
    """
    Normalize player name for consistent matching.
    
    Args:
        name: Raw player name
    
    Returns:
        Normalized name (lowercase, no special chars)
    """
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove suffixes (Jr., Sr., III, etc.)
    name = re.sub(r'\s+(jr\.?|sr\.?|iii?|iv)$', '', name)
    
    # Remove special characters except spaces and hyphens
    name = re.sub(r'[^a-z\s\-]', '', name)
    
    # Normalize whitespace
    name = re.sub(r'\s+', ' ', name.strip())
    
    return name


def chunks(lst: List, n: int) -> List[List]:
    """
    Split list into chunks of size n.
    
    Args:
        lst: List to split
        n: Chunk size
    
    Returns:
        List of chunks
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries (later dicts override earlier).
    
    Args:
        *dicts: Dictionaries to merge
    
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


# Example usage
if __name__ == "__main__":
    """Test helper functions."""
    
    print("Testing Helper Functions")
    print("=" * 50)
    
    # Test safe_get
    test_data = {
        'game': {
            'teams': [
                {'name': 'Chiefs', 'score': 28},
                {'name': '49ers', 'score': 24}
            ]
        }
    }
    
    print("\n1. Testing safe_get:")
    print(f"  Team 0 name: {safe_get(test_data, 'game', 'teams', 0, 'name')}")
    print(f"  Missing key: {safe_get(test_data, 'game', 'missing', 'key', default='N/A')}")
    
    # Test datetime parsing
    print("\n2. Testing datetime parsing:")
    date_str = "2024-09-15T20:00:00Z"
    parsed_date = parse_espn_datetime(date_str)
    print(f"  Parsed: {parsed_date}")
    
    # Test money formatting
    print("\n3. Testing money formatting:")
    print(f"  $15,000,000 → {format_money(15_000_000)}")
    print(f"  $500,000 → {format_money(500_000)}")
    
    # Test percentage calculation
    print("\n4. Testing percentage calculation:")
    print(f"  75/100 = {calculate_percentage(75, 100)}%")
    print(f"  0/0 = {calculate_percentage(0, 0)}%")
    
    # Test player name normalization
    print("\n5. Testing player name normalization:")
    print(f"  'Patrick Mahomes II' → '{normalize_player_name('Patrick Mahomes II')}'")
    print(f"  'Christian McCaffrey' → '{normalize_player_name('Christian McCaffrey')}'")
    
    print("\n" + "=" * 50)
    print("Helper functions test complete!")
