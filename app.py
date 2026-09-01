import os
import sys



import streamlit as st
import pandas as pd
from src.i18n import t
from src.data_loaders.fbref_loader import load_player_season_stats, load_team_season_stats
from src.data_loaders.understat_loader import load_team_shots
from src.visualizers import plot_shot_map, plot_player_radar, plot_team_scatter
from src.progress import run_with_progress

st.set_page_config(page_title=t("app_title"), layout="wide")

st.title(t("app_title"))

# Sidebar
st.sidebar.title(t("sidebar_title"))
module = st.sidebar.radio(t("module_selector"), [
    t("module_scouting"),
    t("module_shots"),
    t("module_teams")
])

leagues_list = ["ESP-La Liga", "ENG-Premier League", "ITA-Serie A", "GER-Bundesliga", "FRA-Ligue 1"]
league = st.sidebar.selectbox(t("league_select"), leagues_list)

seasons_list = ["2627", "2526", "2425", "2324", "2223", "2122", "2021"]
season = st.sidebar.selectbox(t("season_select"), seasons_list)

# App Logic
if module == t("module_scouting"):
    st.header(t("player_radar_title"))

    stats_df = run_with_progress(load_player_season_stats, league, season, estimated_time=20, title=t("loading_data"))

    if not stats_df.empty:
        # Check if Minutes Played exists, adjust the key based on actual fbref flattened columns
        min_mins = st.sidebar.slider(t("min_minutes"), 0, 3000, 450)

        # We need to map actual column names here depending on fbref output.
        # For this prototype, we'll assume standard columns are there.
        # Player names are usually in 'player' column.
        if 'player' in stats_df.columns:
            players = stats_df['player'].dropna().unique().tolist()
            player_a = st.selectbox(t("player_a_select"), players)
            player_b = st.selectbox(t("player_b_select"), players)

            # Placeholder for radar plot (assuming we have percentiles calculated)
            # In a real scenario, you'd calculate percentiles for specific metrics
            metrics = ["Expected Goals (xG)", "Expected Assists (xA)", "Progressive Passes (PrgP)", "Progressive Carries (PrgC)"]

            if st.button("Generar Radar"):
                # Mock percentiles
                stats_a = [80, 60, 70, 90]
                stats_b = [60, 80, 50, 70]
                fig = plot_player_radar(stats_a, stats_b, metrics, metrics, player_a_name=player_a, player_b_name=player_b)
                st.pyplot(fig)
        else:
            st.warning(t("no_data"))

elif module == t("module_shots"):
    st.header(t("shot_map_title"))

    shots_df = run_with_progress(load_team_shots, league, season, estimated_time=10, title=t("loading_data"))

    if not shots_df.empty and 'team' in shots_df.columns:
        teams = shots_df['team'].dropna().unique().tolist()
        team = st.sidebar.selectbox(t("team_select"), teams)

        team_shots = shots_df[shots_df['team'] == team]
        fig = plot_shot_map(team_shots, team)
        st.pyplot(fig)
    else:
        st.warning(t("no_data"))

elif module == t("module_teams"):
    st.header(t("team_scatter_title"))

    team_df = run_with_progress(load_team_season_stats, league, season, estimated_time=20, title=t("loading_data"))

    if not team_df.empty:
        # Map actual columns. Mocking columns for scatter
        cols = team_df.columns.tolist()
        x_col = st.selectbox("Eje X", cols)
        y_col = st.selectbox("Eje Y", cols)

        fig = plot_team_scatter(team_df, x_col, y_col)
        st.pyplot(fig)
    else:
        st.warning(t("no_data"))

