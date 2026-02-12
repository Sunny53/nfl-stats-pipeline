"""
Day 1 - API Extraction Testing Script
Tests ESPN API client and validates data extraction.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from src.extraction.api_client import ESPNAPIClient
from src.utils.logger import setup_logger
from src.utils.helpers import safe_get, parse_espn_datetime


# Setup
logger = setup_logger(__name__)
OUTPUT_DIR = Path("data/raw/day1_test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def test_1_current_scoreboard():
    """Test: Fetch current week's scoreboard."""
    print("\n" + "="*60)
    print("TEST 1: Current Scoreboard")
    print("="*60)
    
    client = ESPNAPIClient()
    
    try:
        scoreboard = client.get_scoreboard()
        
        # Extract key info
        events = scoreboard.get('events', [])
        week = safe_get(scoreboard, 'week', 'number', default='Unknown')
        season = safe_get(scoreboard, 'season', 'year', default='Unknown')
        
        print(f"✓ Season: {season}")
        print(f"✓ Week: {week}")
        print(f"✓ Games found: {len(events)}")
        
        # Save raw data
        output_file = OUTPUT_DIR / f"scoreboard_week{week}.json"
        with open(output_file, 'w') as f:
            json.dump(scoreboard, f, indent=2)
        print(f"✓ Saved to: {output_file}")
        
        # Display sample game
        if events:
            game = events[0]
            game_name = game.get('name', 'Unknown')
            game_date = parse_espn_datetime(game.get('date', ''))
            status = safe_get(game, 'status', 'type', 'description', default='Unknown')
            
            print(f"\nSample Game:")
            print(f"  - {game_name}")
            print(f"  - Date: {game_date}")
            print(f"  - Status: {status}")
            
            # Extract teams and scores
            competitions = safe_get(game, 'competitions', 0, default={})
            competitors = competitions.get('competitors', [])
            
            if len(competitors) >= 2:
                home = competitors[0]
                away = competitors[1]
                
                home_team = safe_get(home, 'team', 'displayName', default='Unknown')
                away_team = safe_get(away, 'team', 'displayName', default='Unknown')
                home_score = safe_get(home, 'score', default='0')
                away_score = safe_get(away, 'score', default='0')
                
                print(f"  - {away_team}: {away_score}")
                print(f"  - {home_team}: {home_score}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Test 1 failed: {e}", exc_info=True)
        return False


def test_2_teams_list():
    """Test: Fetch all NFL teams."""
    print("\n" + "="*60)
    print("TEST 2: NFL Teams List")
    print("="*60)
    
    client = ESPNAPIClient()
    
    try:
        teams = client.get_teams()
        
        print(f"✓ Teams found: {len(teams)}")
        
        # Save teams data
        output_file = OUTPUT_DIR / "teams.json"
        with open(output_file, 'w') as f:
            json.dump(teams, f, indent=2)
        print(f"✓ Saved to: {output_file}")
        
        # Display sample teams
        print(f"\nSample Teams (first 5):")
        for i, team_wrapper in enumerate(teams[:5]):
            team = team_wrapper.get('team', {})
            name = team.get('displayName', 'Unknown')
            abbr = team.get('abbreviation', 'UNK')
            print(f"  {i+1}. {name} ({abbr})")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Test 2 failed: {e}", exc_info=True)
        return False


def test_3_team_roster():
    """Test: Fetch roster for a specific team."""
    print("\n" + "="*60)
    print("TEST 3: Team Roster (Kansas City Chiefs)")
    print("="*60)
    
    client = ESPNAPIClient()
    
    try:
        # Kansas City Chiefs team ID
        team_id = "12"
        
        roster = client.get_team_roster(team_id)
        
        # Extract athletes
        athletes = safe_get(roster, 'athletes', default=[])
        
        print(f"✓ Roster size: {len(athletes)} players")
        
        # Save roster data
        output_file = OUTPUT_DIR / f"roster_team{team_id}.json"
        with open(output_file, 'w') as f:
            json.dump(roster, f, indent=2)
        print(f"✓ Saved to: {output_file}")
        
        # Display sample players
        print(f"\nSample Players (first 5):")
        for i, athlete in enumerate(athletes[:5]):
            name = safe_get(athlete, 'displayName', default='Unknown')
            position = safe_get(athlete, 'position', 'abbreviation', default='UNK')
            jersey = safe_get(athlete, 'jersey', default='--')
            
            print(f"  {i+1}. #{jersey} {name} ({position})")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Test 3 failed: {e}", exc_info=True)
        return False


def test_4_standings():
    """Test: Fetch NFL standings."""
    print("\n" + "="*60)
    print("TEST 4: NFL Standings")
    print("="*60)
    
    client = ESPNAPIClient()
    
    try:
        standings = client.get_standings()
        
        # Save standings data
        output_file = OUTPUT_DIR / "standings.json"
        with open(output_file, 'w') as f:
            json.dump(standings, f, indent=2)
        print(f"✓ Saved to: {output_file}")
        
        # Extract and display sample
        children = safe_get(standings, 'children', default=[])
        
        if children:
            print(f"✓ Conferences found: {len(children)}")
            
            # Show AFC standings sample
            afc = children[0]
            conf_name = safe_get(afc, 'name', default='Unknown')
            standings_list = safe_get(afc, 'standings', 'entries', default=[])
            
            print(f"\n{conf_name} Standings (Top 5):")
            for i, entry in enumerate(standings_list[:5]):
                team = safe_get(entry, 'team', 'displayName', default='Unknown')
                stats = entry.get('stats', [])
                
                # Extract wins/losses
                wins = next((s['value'] for s in stats if s.get('name') == 'wins'), 0)
                losses = next((s['value'] for s in stats if s.get('name') == 'losses'), 0)
                
                print(f"  {i+1}. {team}: {wins}-{losses}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Test 4 failed: {e}", exc_info=True)
        return False


def test_5_historical_data():
    """Test: Fetch games from a date range."""
    print("\n" + "="*60)
    print("TEST 5: Historical Data (Last 7 days)")
    print("="*60)
    
    client = ESPNAPIClient()
    
    try:
        # Get games from last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        print(f"Fetching games from {start_date.date()} to {end_date.date()}...")
        
        games = client.get_games_by_date_range(start_date, end_date)
        
        print(f"✓ Games found: {len(games)}")
        
        # Save historical data
        output_file = OUTPUT_DIR / "historical_7days.json"
        with open(output_file, 'w') as f:
            json.dump(games, f, indent=2)
        print(f"✓ Saved to: {output_file}")
        
        # Display sample
        if games:
            print(f"\nSample Games:")
            for i, game in enumerate(games[:3]):
                game_name = game.get('name', 'Unknown')
                game_date = parse_espn_datetime(game.get('date', ''))
                print(f"  {i+1}. {game_name} - {game_date.date() if game_date else 'Unknown'}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Test 5 failed: {e}", exc_info=True)
        return False


def analyze_extracted_data():
    """Analyze the extracted data structure for database design."""
    print("\n" + "="*60)
    print("DATA STRUCTURE ANALYSIS")
    print("="*60)
    
    scoreboard_file = list(OUTPUT_DIR.glob("scoreboard_*.json"))
    
    if scoreboard_file:
        with open(scoreboard_file[0], 'r') as f:
            data = json.load(f)
        
        print("\nKey Data Points Found:")
        print("-" * 60)
        
        # Analyze game structure
        game = safe_get(data, 'events', 0, default={})
        
        if game:
            print("\n✓ GAME LEVEL:")
            print(f"  - Game ID: {game.get('id', 'N/A')}")
            print(f"  - Name: {game.get('name', 'N/A')}")
            print(f"  - Date: {game.get('date', 'N/A')}")
            print(f"  - Season: {safe_get(game, 'season', 'year', default='N/A')}")
            print(f"  - Week: {safe_get(game, 'week', 'number', default='N/A')}")
            
            competition = safe_get(game, 'competitions', 0, default={})
            
            if competition:
                print("\n✓ COMPETITION LEVEL:")
                print(f"  - Venue: {safe_get(competition, 'venue', 'fullName', default='N/A')}")
                print(f"  - Attendance: {competition.get('attendance', 'N/A')}")
                
                competitors = competition.get('competitors', [])
                
                if competitors:
                    print("\n✓ TEAM LEVEL:")
                    team = safe_get(competitors, 0, 'team', default={})
                    print(f"  - Team ID: {team.get('id', 'N/A')}")
                    print(f"  - Name: {team.get('displayName', 'N/A')}")
                    print(f"  - Abbreviation: {team.get('abbreviation', 'N/A')}")
                    print(f"  - Score: {safe_get(competitors, 0, 'score', default='N/A')}")
                    
                    # Stats
                    stats = safe_get(competitors, 0, 'statistics', default=[])
                    if stats:
                        print(f"\n✓ STATISTICS (sample):")
                        for stat in stats[:5]:
                            print(f"  - {stat.get('name', 'Unknown')}: {stat.get('displayValue', 'N/A')}")
        
        print("\n" + "-" * 60)
        print("\nRecommended Database Tables:")
        print("  1. games (game_id, date, season, week, status)")
        print("  2. teams (team_id, name, abbreviation, conference, division)")
        print("  3. game_stats (game_id, team_id, stat_type, value)")
        print("  4. players (player_id, name, position, team_id)")
        print("  5. player_stats (game_id, player_id, stat_type, value)")


def main():
    """Run all Day 1 tests."""
    print("\n" + "🏈" * 30)
    print("NFL STATS ETL PIPELINE - DAY 1 TESTING")
    print("🏈" * 30)
    
    results = {
        'Test 1 - Scoreboard': test_1_current_scoreboard(),
        'Test 2 - Teams': test_2_teams_list(),
        'Test 3 - Roster': test_3_team_roster(),
        'Test 4 - Standings': test_4_standings(),
        'Test 5 - Historical': test_5_historical_data(),
    }
    
    # Data analysis
    analyze_extracted_data()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print("\n" + "-"*60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("-"*60)
    
    print(f"\n✓ Raw data saved to: {OUTPUT_DIR}")
    print(f"✓ Logs saved to: logs/")
    
    print("\n" + "🏈" * 30)
    print("DAY 1 COMPLETE!")
    print("Next: Day 2 - Database Design & Storage")
    print("🏈" * 30 + "\n")


if __name__ == "__main__":
    main()
