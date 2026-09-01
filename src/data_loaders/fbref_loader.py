import streamlit as st
import soccerdata as sd
import pandas as pd
from ..utils import flatten_multiindex_columns

@st.cache_resource(show_spinner=False)
def get_fbref_instance(leagues, seasons):
    import os
    import tempfile
    try:
        import seleniumbase.core.browser_launcher as bl
        temp_dir = os.path.join(tempfile.gettempdir(), "sb_drivers")
        os.makedirs(temp_dir, exist_ok=True)
        bl.DRIVER_DIR = temp_dir
        bl.LOCAL_UC_DRIVER = os.path.join(temp_dir, "uc_driver")
    except Exception:
        pass
    
    # Initialize with no_cache=False to use local disk cache
    return sd.FBref(leagues=leagues, seasons=seasons, no_cache=False)

@st.cache_data(show_spinner=False, ttl=43200) # Caché de 12 horas
def load_player_season_stats(leagues, seasons, stat_type="standard"):
    try:
        fbref = get_fbref_instance(leagues, seasons)
        df = fbref.read_player_season_stats(stat_type=stat_type)
        return flatten_multiindex_columns(df)
    except Exception as e:
        st.error(f"Error loading player stats ({stat_type}): {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False, ttl=43200) # Caché de 12 horas
def load_team_season_stats(leagues, seasons, stat_type="standard"):
    try:
        fbref = get_fbref_instance(leagues, seasons)
        df = fbref.read_team_season_stats(stat_type=stat_type)
        return flatten_multiindex_columns(df)
    except Exception as e:
        st.error(f"Error loading team stats ({stat_type}): {e}")
        return pd.DataFrame()


