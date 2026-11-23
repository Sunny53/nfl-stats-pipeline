import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from etl.extract import extract_all_data
from etl.transform import transform_data
from etl.load import load_data, check_connection

def run_pipeline():
    print("="*50)
    print("NFL Stats Pipeline")
    print("="*50)
    
    if not check_connection():
        return None, None
    
    # Extract
    weekly = extract_all_data()
    
    # Transform
    players, seasons = transform_data(weekly)
    
    if len(players) == 0:
        print("\nERROR: No data to load!")
        return None, None
    
    # Load
    print("\nLoading to database...")
    load_data(players, seasons)
    
    print("\n" + "="*50)
    try:
        print("OK: Pipeline complete!")
    except UnicodeEncodeError:
        sys.stdout.buffer.write(b"OK: Pipeline complete!\n")
    print("="*50)
    
    return players, seasons

if __name__ == "__main__":
    run_pipeline()