import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from etl import load


def test_load_data_rolls_back_both_tables_when_insert_fails(monkeypatch):
    engine = create_engine("sqlite://")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE dim_players (player_id TEXT PRIMARY KEY, name TEXT)"
        ))
        conn.execute(text(
            "CREATE TABLE fact_player_seasons ("
            "player_id TEXT, season_year INTEGER CHECK (season_year > 0))"
        ))
        conn.execute(text(
            "INSERT INTO dim_players (player_id, name) VALUES ('old', 'Old Player')"
        ))
        conn.execute(text(
            "INSERT INTO fact_player_seasons (player_id, season_year) "
            "VALUES ('old', 2023)"
        ))
    monkeypatch.setattr(load, "get_engine", lambda: engine)

    players = pd.DataFrame([{"player_id": "new", "name": "New Player"}])
    seasons = pd.DataFrame([{"player_id": "new", "season_year": 0}])

    with pytest.raises(IntegrityError):
        load.load_data(players, seasons)

    with engine.connect() as conn:
        assert conn.execute(
            text("SELECT player_id FROM dim_players")
        ).scalars().all() == ["old"]
        assert conn.execute(
            text("SELECT player_id FROM fact_player_seasons")
        ).scalars().all() == ["old"]

    engine.dispose()
