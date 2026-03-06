import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from utils.db import get_leaderboard, search_player, get_player_career_stats
import pandas as pd

st.set_page_config(
    page_title="NFL Clutch Analytics",
    page_icon="🏈",
    layout="wide"
)

st.title("🏈 NFL QB/WR Analytics Dashboard")

with st.expander("📊 About These Metrics", expanded=False):
    st.markdown("""
    ### Snap Efficiency
    **Formula**: `Yards / Real Snaps`
    
    - **QBs**: Passing yards ÷ offensive snaps played
    - **WRs**: Receiving yards ÷ offensive snaps played
    
    Measures how many yards a player produces per snap on the field.
    Higher is better. Uses real snap counts from NFL play-by-play data.
    
    ---
    
    ### Yards Per Attempt
    **Formula**: `Yards / Opportunities`
    
    - **QBs**: Passing yards ÷ pass attempts
    - **WRs**: Receiving yards ÷ targets
    
    Measures production efficiency per opportunity regardless of playing time.
    
    ---
    
    ### Consistency Score
    **Formula**: `max(0, 100 - (CV × 100))`
    
    Calculated from the Coefficient of Variation (CV) of weekly yards:
    - CV = standard deviation of weekly yards ÷ mean weekly yards
    - Higher score = more consistent week-to-week performance
    - Scale: 0 (extremely volatile) → 100 (perfectly consistent)
    - Most NFL players score between 40–75
    
    **Qualifying thresholds**: QB 200+ attempts, WR 40+ targets  
    *Regular season only. Seasons 2015–present.*
    
    ---
    
    ### 🔮 Future Updates
    - **Clutch Performance Index** — performance in high-leverage game situations
    - **Value Per Dollar** — production relative to salary (via OverTheCap)
    - **Fatigue Factor** — impact of short rest, travel distance, and weather conditions
    - **Momentum Shifts** — big play frequency and impact analysis
    - **Real-time data** — migration to RapidAPI for live season updates
    - **Microsoft Power BI** — embedded advanced visual analytics dashboard
    """)

# Sidebar navigation
page = st.sidebar.radio(
    "Select Page",
    ["QB Leaderboards", "WR Leaderboards", "Player Search"]
)

if page == "QB Leaderboards":
    st.header("Quarterback Leaderboards")

    col1, col2 = st.columns(2)
    with col1:
        metric = st.selectbox(
            "Metric",
            options=["Snap Efficiency", "Consistency Score"],
            index=0,
            key="qb_metric"
        )
    with col2:
        split = st.selectbox(
            "Time Period",
            options=["1yr", "5yr", "Career"],
            index=0,
            key="qb_split"
        )

    try:
        df = get_leaderboard("QB", metric, split)

        st.subheader(f"{metric} - {split}")

        df_display = df[['rank', 'name', 'period', 'value']].copy()
        df_display.columns = ['Rank', 'Player', 'Period', 'Score']

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )

        top_10 = df.head(10)
        st.bar_chart(
            data=top_10.set_index('name')['value'],
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Error loading data: {e}")

elif page == "WR Leaderboards":
    st.header("Wide Receiver Leaderboards")

    col1, col2 = st.columns(2)
    with col1:
        metric = st.selectbox(
            "Metric",
            options=["Snap Efficiency", "Consistency Score"],
            index=0,
            key="wr_metric"
        )
    with col2:
        split = st.selectbox(
            "Time Period",
            options=["1yr", "5yr", "Career"],
            index=0,
            key="wr_split"
        )

    try:
        df = get_leaderboard("WR", metric, split)

        st.subheader(f"{metric} - {split}")

        df_display = df[['rank', 'name', 'period', 'value']].copy()
        df_display.columns = ['Rank', 'Player', 'Period', 'Score']

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )

        top_10 = df.head(10)
        st.bar_chart(
            data=top_10.set_index('name')['value'],
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Error loading data: {e}")

else:  # Player Search
    st.header("Player Search")

    search_term = st.text_input("Search for a player", placeholder="e.g., Mahomes, Jefferson")

    if search_term:
        try:
            results = search_player(search_term)

            if results.empty:
                st.warning("No players found")
            else:
                players = results[['player_id', 'name', 'position']].drop_duplicates()

                for _, player in players.iterrows():
                    with st.expander(f"{player['name']} ({player['position']})"):
                        player_data = results[results['player_id'] == player['player_id']]

                        if player_data.empty:
                            st.warning("No season data available")
                            continue

                        player_data = player_data.dropna(subset=['yards', 'tds'])

                        if player_data.empty:
                            st.warning("Incomplete data for this player")
                            continue

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Career Seasons", len(player_data))
                        with col2:
                            avg_eff = player_data['snap_efficiency'].mean()
                            st.metric("Avg Snap Efficiency", f"{avg_eff:.2f}" if pd.notna(avg_eff) else "N/A")
                        with col3:
                            avg_con = player_data['consistency_score'].mean()
                            st.metric("Avg Consistency", f"{avg_con:.1f}" if pd.notna(avg_con) else "N/A")

                        st.line_chart(
                            player_data.set_index('season_year')[['snap_efficiency', 'consistency_score']],
                            use_container_width=True
                        )

                        st.dataframe(
                            player_data[['season_year', 'team', 'games', 'yards', 'tds', 'snap_efficiency', 'consistency_score']],
                            hide_index=True
                        )

        except Exception as e:
            st.error(f"Error searching: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit + Supabase")