import streamlit as st
import soccerdata as sd
import pandas as pd

@st.cache_data(show_spinner=False)
def get_understat_instance(leagues, seasons):
    return sd.Understat(leagues=leagues, seasons=seasons, no_cache=False)

@st.cache_data(show_spinner=False)
def load_team_shots(leagues, seasons):
    try:
        us = get_understat_instance(leagues, seasons)
        # Assuming read_team_match_stats or similar exist, but typically for shots we read match shots.
        # However, read_shots gives shots for a team/match.
        df = us.read_shots()
        return df
    except Exception as e:
        st.error(f"Error loading Understat shots: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_match_shots(leagues, seasons, match_id):
    # This is a placeholder since soccerdata's read_shots gets all loaded matches
    df = load_team_shots(leagues, seasons)
    if not df.empty and 'game_id' in df.columns:
        return df[df['game_id'] == match_id]
    return pd.DataFrame()

