import nflreadpy as nfl
df = nfl.load_snap_counts([2023])
ids = nfl.load_ff_playerids()
snaps = nfl.load_snap_counts([2015, 2016])
weekly = nfl.load_player_stats([2023])
print(weekly['season_type'].unique())