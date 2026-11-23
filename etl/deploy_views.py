import sys
from pathlib import Path

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from etl.load import get_engine


if __name__ == "__main__":
    sql_path = PROJECT_ROOT / "database" / "views.sql"
    sql = sql_path.read_text(encoding="utf-8")
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(sql))
    try:
        print("OK: Views created successfully!")
    except UnicodeEncodeError:
        sys.stdout.buffer.write(b"OK: Views created successfully!\n")