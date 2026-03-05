import nfl_data_py as nfl
df = nfl.import_snap_counts([2023])
ids = nfl.import_ids()
snaps = nfl.import_snap_counts([2015, 2016])
weekly = nfl.import_weekly_data([2023])
print(weekly['season_type'].unique())