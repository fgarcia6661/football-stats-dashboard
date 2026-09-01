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

# --- Module: Scouting / Radar ---
if module == t("module_scouting"):
    st.header(t("player_radar_title"))
    stats_df = run_with_progress(load_player_season_stats, league, season, estimated_time=20, title=t("loading_data"))

    if not stats_df.empty:
        # Detect player column (could be 'Player' or 'player' depending on source)
        player_col = next((c for c in stats_df.columns if c.lower() == "player"), None)

        # Detect minutes column and get its max to calibrate the slider
        min_col = next((c for c in stats_df.columns if c.lower() == "playing time_min"), None)
        if min_col:
            stats_df[min_col] = pd.to_numeric(
                stats_df[min_col].astype(str).str.replace(",", ""), errors="coerce"
            ).fillna(0)
            max_minutes = int(stats_df[min_col].max())
        else:
            max_minutes = 3000

        # Default to 10% of max, so early-season data is not filtered out
        default_min = max(0, min(450, max_minutes // 4))
        min_mins = st.sidebar.slider(t("min_minutes"), 0, max(max_minutes, 1), default_min)

        if player_col:
            players = sorted(stats_df[player_col].dropna().astype(str).unique().tolist())
            player_a = st.selectbox(t("player_a_select"), players, index=0)
            player_b = st.selectbox(t("player_b_select"), players, index=min(1, len(players) - 1))

            metrics = ["Performance_Gls", "Performance_Ast", "Per 90 Minutes_Gls", "Per 90 Minutes_Ast"]
            metric_labels = ["Goles", "Asistencias", "Goles p/90", "Asistencias p/90"]

            if st.button("Generar Radar"):
                # Apply minutes filter (min_col already converted to numeric above)
                if min_col:
                    valid_players = stats_df[stats_df[min_col] >= min_mins].copy()
                else:
                    valid_players = stats_df.copy()

                if valid_players.empty:
                    st.error(f"⚠️ Ningún jugador supera {min_mins} minutos. Baja el filtro de minutos mínimos en la barra lateral.")
                else:
                    for m in metrics:
                        if m in valid_players.columns:
                            valid_players[m] = pd.to_numeric(valid_players[m], errors="coerce").fillna(0)
                            valid_players[f"{m}_pct"] = valid_players[m].rank(pct=True) * 100
                        else:
                            valid_players[f"{m}_pct"] = 0

                    p_a = valid_players[valid_players[player_col] == player_a]
                    p_b = valid_players[valid_players[player_col] == player_b]

                    if p_a.empty:
                        st.error(f"⚠️ {player_a} no tiene suficientes minutos para aparecer en el radar. Baja el filtro.")
                    elif p_b.empty:
                        st.error(f"⚠️ {player_b} no tiene suficientes minutos para aparecer en el radar. Baja el filtro.")
                    else:
                        stats_a = [float(p_a[f"{m}_pct"].values[0]) for m in metrics]
                        stats_b = [float(p_b[f"{m}_pct"].values[0]) for m in metrics]

                        fig = plot_player_radar(stats_a, stats_b, metric_labels, metric_labels, player_a_name=player_a, player_b_name=player_b)
                        st.pyplot(fig)
        else:
            st.warning(t("no_data"))
    else:
        st.warning(t("no_data"))

# --- Module: Shot Map ---
elif module == t("module_shots"):
    st.header(t("shot_map_title"))
    shots_df = run_with_progress(load_team_shots, league, season, estimated_time=20, title=t("loading_data"))

    if not shots_df.empty and "team" in shots_df.columns:
        teams = shots_df["team"].dropna().unique().tolist()
        team = st.sidebar.selectbox(t("team_select"), teams)
        team_shots = shots_df[shots_df["team"] == team]
        fig = plot_shot_map(team_shots, team)
        st.pyplot(fig)
    else:
        st.warning(t("no_data"))

# --- Module: Team Metrics ---
elif module == t("module_teams"):
    st.header(t("team_scatter_title"))
    team_df = run_with_progress(load_team_season_stats, league, season, estimated_time=20, title=t("loading_data"))

    if not team_df.empty:
        cols = team_df.columns.tolist()
        x_col = st.selectbox("Eje X", cols)
        y_col = st.selectbox("Eje Y", cols)
        fig = plot_team_scatter(team_df, x_col, y_col)
        st.pyplot(fig)
    else:
        st.warning(t("no_data"))
