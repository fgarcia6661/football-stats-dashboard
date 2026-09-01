TRANSLATIONS = {
    # Selectors and Navigation
    "app_title": "Dashboard de Análisis y Scouting de Fútbol en Vivo",
    "sidebar_title": "Navegación",
    "module_selector": "Seleccionar Módulo",
    "module_scouting": "Scouting y Radares de Jugadores",
    "module_shots": "Mapa de Tiros (xG)",
    "module_teams": "Métricas de Equipos",
    "league_select": "Seleccionar Liga",
    "season_select": "Seleccionar Temporada",
    "team_select": "Seleccionar Equipo",
    "player_select": "Seleccionar Jugador",
    "player_a_select": "Jugador A",
    "player_b_select": "Jugador B",
    "position_select": "Demarcación / Posición",
    "min_minutes": "Minutos mínimos jugados",

    # Module Titles
    "shot_map_title": "Mapa de Tiros",
    "player_radar_title": "Comparador de Jugadores (Radar)",
    "team_scatter_title": "Matriz de Rendimiento de Equipos",

    # Metrics
    "Expected Goals (xG)": "Goles Esperados (xG)",
    "Expected Assists (xA)": "Asistencias Esperadas (xA)",
    "Progressive Passes (PrgP)": "Pases Progresivos",
    "Progressive Carries (PrgC)": "Conducciones Progresivas",
    "Shot-Creating Actions (SCA)": "Acciones de Creación de Tiro",
    "Tackles + Interceptions (Tkl+Int)": "Entradas + Intercepciones",
    "Minutes Played": "Minutos Jugados",
    "Goals": "Goles",
    "Shots": "Tiros",
    "xG": "xG",
    "xA": "xA",
    "Ast": "Asistencias",

    # Shot Outcomes
    "Goal": "Gol",
    "Saved": "Parado",
    "Missed": "Fuera",
    "Blocked": "Bloqueado",

    # Teams / Positions
    "FW": "Delanteros",
    "MF": "Centrocampistas",
    "DF": "Defensas",
    "GK": "Porteros",

    # General
    "loading_data": "Cargando datos, por favor espera...",
    "insufficient_minutes": "Advertencia: El jugador no alcanza el mínimo de minutos disputados.",
    "no_data": "No hay datos disponibles para la selección actual.",
}

def t(key: str) -> str:
    """Traduce la clave al castellano de España si existe, de lo contrario devuelve la clave."""
    return TRANSLATIONS.get(key, key)

