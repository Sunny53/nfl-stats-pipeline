"""
ESPN API Client with robust error handling and retry logic.
Handles rate limiting, network errors, and data validation.
"""

import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from src.config import ESPNEndpoints, settings
from src.utils.logger import setup_logger, log_api_request, log_api_response


logger = setup_logger(__name__)


class ESPNAPIError(Exception):
    """Custom exception for ESPN API errors."""
    pass


class ESPNAPIClient:
    """
    Client for ESPN's unofficial NFL API.
    Handles requests with automatic retry, rate limiting, and error handling.
    """
    
    def __init__(self):
        self.base_url = settings.espn_api_base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        self.last_request_time = None
        self.min_request_interval = 0.5  # 500ms between requests (rate limiting)
    
    def _rate_limit(self):
        """Enforce minimum time between requests to avoid rate limiting."""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                sleep_time = self.min_request_interval - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, ESPNAPIError)),
        reraise=True
    )
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            endpoint: API endpoint URL
            params: Query parameters
        
        Returns:
            JSON response as dictionary
        
        Raises:
            ESPNAPIError: If request fails after retries
        """
        self._rate_limit()
        
        start_time = time.time()
        log_api_request(logger, endpoint, params)
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response_time = time.time() - start_time
            
            log_api_response(logger, endpoint, response.status_code, response_time)
            
            # Check for HTTP errors
            if response.status_code == 429:
                logger.warning("Rate limited by ESPN API, will retry...")
                raise ESPNAPIError("Rate limited")
            
            response.raise_for_status()
            
            # Parse JSON
            try:
                data = response.json()
                logger.debug(f"Successfully fetched data from {endpoint}")
                return data
            except ValueError as e:
                logger.error(f"Invalid JSON response from {endpoint}: {e}")
                raise ESPNAPIError(f"Invalid JSON response: {e}")
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout requesting {endpoint}")
            raise ESPNAPIError("Request timeout")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error requesting {endpoint}: {e}")
            raise ESPNAPIError(f"Connection error: {e}")
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {response.status_code} from {endpoint}: {e}")
            raise ESPNAPIError(f"HTTP {response.status_code}: {e}")
    
    def get_scoreboard(
        self,
        season: Optional[int] = None,
        week: Optional[int] = None,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get scoreboard data (games and scores).
        
        Args:
            season: NFL season year (default: current season)
            week: Week number (1-18 for regular season)
            date: Specific date in YYYYMMDD format
        
        Returns:
            Scoreboard data including games, scores, and team stats
        """
        params = {}
        
        if season:
            params['season'] = season
        if week:
            params['week'] = week
        if date:
            params['dates'] = date
        
        data = self._make_request(ESPNEndpoints.SCOREBOARD, params)
        
        logger.info(
            f"Fetched scoreboard: {len(data.get('events', []))} games",
            extra={
                'games_count': len(data.get('events', [])),
                'season': season or 'current',
                'week': week or 'current'
            }
        )
        
        return data
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """
        Get list of all NFL teams.
        
        Returns:
            List of team objects with metadata
        """
        data = self._make_request(ESPNEndpoints.TEAMS)
        
        teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
        
        logger.info(f"Fetched {len(teams)} teams")
        return teams
    
    def get_team_roster(self, team_id: str) -> Dict[str, Any]:
        """
        Get roster for a specific team.
        
        Args:
            team_id: ESPN team ID
        
        Returns:
            Team roster data with player information
        """
        endpoint = ESPNEndpoints.TEAM_ROSTER.format(team_id=team_id)
        data = self._make_request(endpoint)
        
        logger.info(f"Fetched roster for team {team_id}")
        return data
    
    def get_team_schedule(self, team_id: str, season: Optional[int] = None) -> Dict[str, Any]:
        """
        Get schedule for a specific team.
        
        Args:
            team_id: ESPN team ID
            season: Season year
        
        Returns:
            Team schedule with game results
        """
        endpoint = ESPNEndpoints.SCHEDULE.format(team_id=team_id)
        params = {'season': season} if season else {}
        
        data = self._make_request(endpoint, params)
        
        logger.info(f"Fetched schedule for team {team_id}")
        return data
    
    def get_standings(self, season: Optional[int] = None) -> Dict[str, Any]:
        """
        Get NFL standings.
        
        Args:
            season: Season year
        
        Returns:
            Conference and division standings
        """
        params = {'season': season} if season else {}
        data = self._make_request(ESPNEndpoints.STANDINGS, params)
        
        logger.info("Fetched NFL standings")
        return data
    
    def get_current_week(self) -> int:
        """
        Determine current NFL week from scoreboard data.
        
        Returns:
            Current week number
        """
        scoreboard = self.get_scoreboard()
        
        # Extract week from scoreboard metadata
        week = scoreboard.get('week', {}).get('number', 1)
        
        logger.info(f"Current NFL week: {week}")
        return week
    
    def get_season_type(self) -> str:
        """
        Determine current season type (preseason, regular, postseason).
        
        Returns:
            Season type string
        """
        scoreboard = self.get_scoreboard()
        season_type = scoreboard.get('season', {}).get('type', 2)
        
        # ESPN API codes: 1=preseason, 2=regular, 3=postseason
        type_map = {
            1: 'preseason',
            2: 'regular',
            3: 'postseason'
        }
        
        return type_map.get(season_type, 'regular')
    
    def get_games_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get all games within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            List of game objects
        """
        all_games = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y%m%d')
            
            try:
                scoreboard = self.get_scoreboard(date=date_str)
                games = scoreboard.get('events', [])
                all_games.extend(games)
                
                logger.debug(f"Found {len(games)} games on {date_str}")
            
            except ESPNAPIError as e:
                logger.warning(f"Error fetching games for {date_str}: {e}")
            
            current_date += timedelta(days=1)
            time.sleep(0.5)  # Extra rate limiting for bulk requests
        
        logger.info(f"Fetched {len(all_games)} games from {start_date} to {end_date}")
        return all_games
    
    def validate_response(self, data: Dict[str, Any], required_keys: List[str]) -> bool:
        """
        Validate API response contains required keys.
        
        Args:
            data: API response data
            required_keys: List of required keys
        
        Returns:
            True if valid, False otherwise
        """
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            logger.warning(f"Response missing required keys: {missing_keys}")
            return False
        
        return True


# Example usage and testing
if __name__ == "__main__":
    """Test ESPN API client functionality."""
    
    print("Testing ESPN API Client...")
    print("=" * 50)
    
    # Initialize client
    client = ESPNAPIClient()
    
    # Test 1: Get current scoreboard
    print("\n1. Fetching current scoreboard...")
    try:
        scoreboard = client.get_scoreboard()
        games = scoreboard.get('events', [])
        print(f"✓ Found {len(games)} games")
        
        if games:
            game = games[0]
            print(f"  Sample game: {game.get('name', 'Unknown')}")
            print(f"  Status: {game.get('status', {}).get('type', {}).get('description', 'Unknown')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Get teams
    print("\n2. Fetching NFL teams...")
    try:
        teams = client.get_teams()
        print(f"✓ Found {len(teams)} teams")
        
        if teams:
            team = teams[0].get('team', {})
            print(f"  Sample team: {team.get('displayName', 'Unknown')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Get current week
    print("\n3. Determining current week...")
    try:
        week = client.get_current_week()
        print(f"✓ Current week: {week}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Get standings
    print("\n4. Fetching standings...")
    try:
        standings = client.get_standings()
        print(f"✓ Standings fetched successfully")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("API Client test complete!")
    print("Check logs/ directory for detailed logging output.")
