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

        # Default to 0 if early season (not enough data), 450 for full seasons
        default_min = 0 if max_minutes < 450 else 450
        min_mins = st.sidebar.slider(t("min_minutes"), 0, max(max_minutes, 1), default_min)

        if player_col:
            players = sorted(stats_df[player_col].dropna().astype(str).unique().tolist())
            
            # Selector de jugadores
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                player_a = st.selectbox(t("player_a_select"), players, index=0)
            with col_sel2:
                player_b = st.selectbox(t("player_b_select"), players, index=min(1, len(players) - 1))

            st.info("ℹ️ **Nota sobre métricas:** Las estadísticas de xG, xA y Presiones ya no son de acceso gratuito en ciertas ligas de FBref. Se han añadido métricas avanzadas equivalentes (defensa, posesión y pases).")

            if "Performance_Gls" in stats_df.columns and "Performance_Ast" in stats_df.columns and min_col:
                g_a = pd.to_numeric(stats_df["Performance_Gls"], errors="coerce").fillna(0) + pd.to_numeric(stats_df["Performance_Ast"], errors="coerce").fillna(0)
                mins = pd.to_numeric(stats_df[min_col], errors="coerce").fillna(0)
                # Avoid division by zero by setting to 9999 or max
                stats_df["Min_por_G_A"] = (mins / g_a.replace(0, pd.NA)).fillna(9999)

            # Diccionario de métricas disponibles (etiqueta amigable -> columna FBref)
            AVAILABLE_METRICS = {
                "Goles": "Performance_Gls",
                "Asistencias": "Performance_Ast",
                "Minutos por G/A": "Min_por_G_A",
                "Goles p/90": "Per 90 Minutes_Gls",
                "Entradas (Tackles)": "Tackles_Tkl",
                "Acierto Pases (%)": "Total_Cmp%",
                "Progresión Pases (Dist)": "Total_PrgDist",
                "Regates intentados": "Take-Ons_Att",
                "Regates acertados": "Take-Ons_Succ",
                "Intercepciones": "Int",
                "Despejes (Clearances)": "Clr",
                "Duelos def. ganados (%)": "Challenges_Tkl%",
                "Acciones def. (Tkl+Int)": "Tkl+Int",
                "Recuperaciones": "Rec"
            }

            # Filtrar solo las que existen realmente en el dataframe
            valid_metric_keys = [k for k, v in AVAILABLE_METRICS.items() if v in stats_df.columns]
            
            # Dejar que el usuario elija
            selected_metric_labels = st.multiselect(
                "Seleccionar métricas para el radar (orden agujas del reloj):", 
                options=valid_metric_keys,
                default=valid_metric_keys[:6] if len(valid_metric_keys) >= 6 else valid_metric_keys
            )

            if st.button("Generar Radar"):
                if len(selected_metric_labels) < 3:
                    st.error("⚠️ Debes seleccionar al menos 3 métricas para dibujar un radar.")
                else:
                    if min_col:
                        valid_players = stats_df[stats_df[min_col] >= min_mins].copy()
                    else:
                        valid_players = stats_df.copy()

                    if valid_players.empty:
                        st.error(f"⚠️ Ningún jugador supera {min_mins} minutos. Baja el filtro de minutos mínimos en la barra lateral.")
                    else:
                        metrics = []
                        metric_labels = []
                        missing_metrics = []

                        for k in selected_metric_labels:
                            m = AVAILABLE_METRICS[k]
                            # Limpiar cadenas como '%' y convertir a numérico, manteniendo NaN primero
                            valid_players[m] = pd.to_numeric(valid_players[m].astype(str).str.replace("%", ""), errors="coerce")
                            
                            # Si toda la columna es NaN (FBref no provee este dato)
                            if valid_players[m].isna().all():
                                missing_metrics.append(k)
                            else:
                                metrics.append(m)
                                metric_labels.append(k)

                        if missing_metrics:
                            st.warning(f"⚠️ Las siguientes métricas no están disponibles en la base de datos para esta liga/temporada y se omitirán: {', '.join(missing_metrics)}. FBref/Opta ha retirado estos datos de sus tablas públicas.")

                        if len(metrics) < 3:
                            st.error("⚠️ No hay suficientes métricas con datos reales (mínimo 3) para dibujar el radar.")
                            st.stop()

                        for m in metrics:
                            valid_players[m] = valid_players[m].fillna(0)
                            if m == "Min_por_G_A":
                                # Invertir el ranking: menos minutos es mejor
                                valid_players[f"{m}_pct"] = valid_players[m].rank(pct=True, ascending=False) * 100
                            else:
                                valid_players[f"{m}_pct"] = valid_players[m].rank(pct=True) * 100

                        p_a = valid_players[valid_players[player_col] == player_a]
                        p_b = valid_players[valid_players[player_col] == player_b]

                        if p_a.empty:
                            st.error(f"⚠️ {player_a} no tiene suficientes minutos para aparecer en el radar.")
                        elif p_b.empty:
                            st.error(f"⚠️ {player_b} no tiene suficientes minutos para aparecer en el radar.")
                        else:
                            stats_a_pct = [float(p_a[f"{m}_pct"].values[0]) for m in metrics]
                            stats_b_pct = [float(p_b[f"{m}_pct"].values[0]) for m in metrics]
                            
                            def format_raw(val, metric):
                                if metric == "Min_por_G_A" and val >= 9999: return "-"
                                if pd.isna(val): return "-"
                                return f"{float(val):.2f}".rstrip('0').rstrip('.')

                            stats_a_raw = [format_raw(p_a[m].values[0], m) for m in metrics]
                            stats_b_raw = [format_raw(p_b[m].values[0], m) for m in metrics]

                            col1, col2 = st.columns([1.5, 1])
                            
                            with col1:
                                fig = plot_player_radar(stats_a_pct, stats_b_pct, metric_labels, metric_labels, player_a_name=player_a, player_b_name=player_b)
                                st.pyplot(fig, use_container_width=True)
                                
                            with col2:
                                st.markdown("### Tabla Comparativa (Valores Absolutos)")
                                comp_df = pd.DataFrame({
                                    "Métrica": metric_labels,
                                    player_a: stats_a_raw,
                                    player_b: stats_b_raw
                                })
                                st.dataframe(comp_df, hide_index=True, use_container_width=True)
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
