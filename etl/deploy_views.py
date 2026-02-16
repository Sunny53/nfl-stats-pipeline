import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from etl.load import execute_sql_file

if __name__ == "__main__":
    execute_sql_file('database/views.sql')
    print("✅ Views created successfully!")