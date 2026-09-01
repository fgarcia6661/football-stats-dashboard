import matplotlib.pyplot as plt
from mplsoccer import Pitch, Radar
import seaborn as sns
from .i18n import t
import numpy as np

def plot_shot_map(shots_df, team_name):
    # Setup the pitch
    pitch = Pitch(pitch_type='understat', pitch_color='#1e1e1e', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.patch.set_facecolor('#1e1e1e')

    if shots_df.empty:
        ax.text(0.5, 0.5, t("no_data"), color='white', ha='center', va='center', fontsize=15)
        return fig

    # Map results to colors
    result_colors = {
        'Goal': 'green',
        'SavedShot': 'blue',
        'MissedShots': 'red',
        'BlockedShot': 'yellow',
        'ShotOnPost': 'orange'
    }

    # Filter out null coordinates just in case
    shots_df = shots_df.dropna(subset=['X', 'Y'])

    for _, shot in shots_df.iterrows():
        x = shot.get('X', 0.5)
        y = shot.get('Y', 0.5)
        xg = shot.get('xG', 0.1)
        result = shot.get('result', 'MissedShots')
        color = result_colors.get(result, 'white')

        # Scale marker by xG
        pitch.scatter(x, y, s=xg * 500, c=color, alpha=0.7, ax=ax, edgecolors='black')

    ax.set_title(f"{t('shot_map_title')} - {team_name}", color='white', fontsize=18)
    return fig

def plot_player_radar(player_a_stats, player_b_stats, metrics, params_dict):
    """
    player_a_stats and player_b_stats are lists/arrays of percentiles (0-100).
    """
    # Names for the params
    params = [t(p) for p in params_dict]

    # Radar setup
    radar = Radar(
        params=params,
        min_range=[0]*len(params),
        max_range=[100]*len(params),
        lower_is_better=[],
        round_int=[True]*len(params),
        num_rings=4, ring_width=1, center_circle_radius=1
    )

    fig, ax = radar.setup_axis(figsize=(8, 8), facecolor='#1e1e1e')
    fig.patch.set_facecolor('#1e1e1e')

    # Draw radar
    rings_inner = radar.draw_circles(ax=ax, facecolor='#282a2d', edgecolor='#393b40')
    radar_output = radar.draw_radar_compare(
        player_a_stats, player_b_stats, ax=ax,
        kwargs_radar={'facecolor': '#1f77b4', 'alpha': 0.6},
        kwargs_compare={'facecolor': '#d62728', 'alpha': 0.6}
    )
    radar_poly, radar_poly2, vertices1, vertices2 = radar_output

    # Labels
    range_labels = radar.draw_range_labels(ax=ax, fontsize=10, color='white')
    param_labels = radar.draw_param_labels(ax=ax, fontsize=12, color='white')

    return fig

def plot_team_scatter(teams_df, x_col, y_col):
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#1e1e1e')

    if teams_df.empty or x_col not in teams_df.columns or y_col not in teams_df.columns:
        ax.text(0.5, 0.5, t("no_data"), color='white', ha='center', va='center', fontsize=15)
        return fig

    sns.scatterplot(data=teams_df, x=x_col, y=y_col, ax=ax, color='cyan', s=100)

    # Add labels
    for _, row in teams_df.iterrows():
        team_name = row.name if isinstance(row.name, str) else row.get('team', '')
        ax.text(row[x_col], row[y_col], team_name, color='white', fontsize=9)

    ax.set_xlabel(t(x_col), color='white', fontsize=12)
    ax.set_ylabel(t(y_col), color='white', fontsize=12)
    ax.tick_params(colors='white')

    # Grid
    ax.grid(True, color='#393b40', linestyle='--', alpha=0.5)

    return fig

