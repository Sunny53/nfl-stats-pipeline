import pandas as pd

def calculate_snap_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['snap_efficiency'] = df.apply(
        lambda row: row['yards'] / row['snaps'] if row['snaps'] > 0 else 0,
        axis=1
    ).round(4)
    return df

def calculate_volume_stats(df: pd.DataFrame) -> pd.DataFrame:
    # This is now in transform.py, keep for compatibility
    return df