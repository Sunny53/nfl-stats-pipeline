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
st.markdown("Advanced metrics for quarterback and wide receiver performance")

# Sidebar navigation
page = st.sidebar.radio(
    "Select Page",
    ["QB Leaderboards", "WR Leaderboards", "Player Search"]
)

if page == "QB Leaderboards":
    st.header("Quarterback Leaderboards")
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
        metric = st.selectbox(
            "Metric",
            ["Snap Efficiency", "Consistency Score"]
        )
    with col2:
        split = st.selectbox(
            "Time Period",
            ["1yr", "5yr", "Career"]
        )
    
    # Load data
    try:
        df = get_leaderboard("QB", metric, split)
        
        # Display
        st.subheader(f"{metric} - {split}")
        
        # Format table
        df_display = df[['rank', 'name', 'period', 'value']].copy()
        df_display.columns = ['Rank', 'Player', 'Period', 'Score']
        
        st.dataframe(
            df_display,
            width='stretch',
            hide_index=True
        )
        
        # Top 10 bar chart
        top_10 = df.head(10)
        st.bar_chart(
            data=top_10.set_index('name')['value'],
            width='stretch'
        )
        
    except Exception as e:
        st.error(f"Error loading data: {e}")

elif page == "WR Leaderboards":
    st.header("Wide Receiver Leaderboards")
    
    col1, col2 = st.columns(2)
    with col1:
        metric = st.selectbox(
            "Metric",
            ["Snap Efficiency", "Consistency Score"]
        )
    with col2:
        split = st.selectbox(
            "Time Period",
            ["1yr", "5yr", "Career"]
        )
    
    try:
        df = get_leaderboard("WR", metric, split)
        
        st.subheader(f"{metric} - {split}")
        
        df_display = df[['rank', 'name', 'period', 'value']].copy()
        df_display.columns = ['Rank', 'Player', 'Period', 'Score']
        
        st.dataframe(
            df_display,
            width='stretch',
            hide_index=True
        )
        
        top_10 = df.head(10)
        st.bar_chart(
            data=top_10.set_index('name')['value'],
            width='stretch'
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
                # Get unique players
                players = results[['player_id', 'name', 'position']].drop_duplicates()
                
                for _, player in players.iterrows():
                    with st.expander(f"{player['name']} ({player['position']})"):
                        player_data = results[results['player_id'] == player['player_id']]
                        
                        # Handle missing data
                    if player_data.empty:
                        st.warning("No season data available")
                    continue
            
                        # Drop rows with missing yards/tds for display
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
                        
                        # Career timeline
                        st.line_chart(
                            player_data.set_index('season_year')[['snap_efficiency', 'consistency_score']],
                            width='stretch'
                        )
                        
                        # Raw data
                        st.dataframe(
                            player_data[['season_year', 'team', 'games', 'yards', 'tds', 'snap_efficiency', 'consistency_score']],
                            hide_index=True
                        )
                        
        except Exception as e:
            st.error(f"Error searching: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit + Supabase")