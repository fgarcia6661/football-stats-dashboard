import streamlit as st
import soccerdata as sd
import pandas as pd
from ..utils import flatten_multiindex_columns

@st.cache_data(show_spinner=False)
def get_fbref_instance(leagues, seasons):
    # Initialize with no_cache=False to use local disk cache
    return sd.FBref(leagues=leagues, seasons=seasons, no_cache=False)

@st.cache_data(show_spinner=False)
def load_player_season_stats(leagues, seasons, stat_type="standard"):
    try:
        fbref = get_fbref_instance(leagues, seasons)
        df = fbref.read_player_season_stats(stat_type=stat_type)
        return flatten_multiindex_columns(df)
    except Exception as e:
        st.error(f"Error loading player stats ({stat_type}): {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_team_season_stats(leagues, seasons, stat_type="standard"):
    try:
        fbref = get_fbref_instance(leagues, seasons)
        df = fbref.read_team_season_stats(stat_type=stat_type)
        return flatten_multiindex_columns(df)
    except Exception as e:
        st.error(f"Error loading team stats ({stat_type}): {e}")
        return pd.DataFrame()

