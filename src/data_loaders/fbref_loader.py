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

    # Set data_dir to an absolute local folder so we can commit the cache to GitHub
    from pathlib import Path
    base_dir = Path(__file__).parent.parent.parent
    cache_dir = base_dir / "soccerdata_cache"
    return sd.FBref(leagues=leagues, seasons=seasons, no_cache=False, data_dir=cache_dir)

@st.cache_data(show_spinner=False, ttl=43200, max_entries=1) # Caché de 12 horas, max 1 para ahorrar RAM
def load_player_season_stats(leagues, seasons, stat_type="standard"):
    try:
        from pathlib import Path
        from lxml import html as lxml_html
        import io

        base_dir = Path(__file__).parent.parent.parent
        cache_dir = base_dir / "soccerdata_cache"
        filepath = cache_dir / f"players_{leagues}_{seasons}_{stat_type}.html"

        if filepath.exists():
            # Parse directly from the cached HTML — no webdriver needed
            with open(filepath, "r", encoding="utf-8") as f:
                tree = lxml_html.parse(f)
            for comment in tree.xpath("//comment()"):
                if f"div_stats_{stat_type}" in comment.text:
                    df = pd.read_html(io.StringIO(comment.text), header=[0, 1])[0]
                    # Flatten MultiIndex columns (same as flatten_multiindex_columns)
                    df.columns = [
                        "_".join([str(x) for x in col if str(x) != "" and "Unnamed" not in str(x)]).strip()
                        for col in df.columns.values
                    ]
                    df = df.reset_index(drop=True)
                    # Drop sub-header rows (where 'Player' == 'Player')
                    if "Player" in df.columns:
                        df = df[df["Player"] != "Player"].reset_index(drop=True)
                    return df
            raise ValueError(f"No stats table found in {filepath}")
        else:
            raise FileNotFoundError(f"Cache file not found: {filepath.absolute()}")
    except Exception as e:
        st.error(f"Error loading player stats ({stat_type}): {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False, ttl=43200, max_entries=1) # Caché de 12 horas
def load_team_season_stats(leagues, seasons, stat_type="standard"):
    try:
        from pathlib import Path
        from lxml import html as lxml_html
        import io

        base_dir = Path(__file__).parent.parent.parent
        cache_dir = base_dir / "soccerdata_cache"
        filepath = cache_dir / f"teams_{leagues}_{seasons}_{stat_type}.html"

        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                tree = lxml_html.parse(f)
            for comment in tree.xpath("//comment()"):
                if "div_stats" in comment.text and "squads" in comment.text:
                    df = pd.read_html(io.StringIO(comment.text), header=[0, 1])[0]
                    df.columns = [
                        "_".join([str(x) for x in col if str(x) != "" and "Unnamed" not in str(x)]).strip()
                        for col in df.columns.values
                    ]
                    df = df.reset_index(drop=True)
                    if "Squad" in df.columns:
                        df = df[df["Squad"] != "Squad"].reset_index(drop=True)
                    return df
            raise ValueError(f"No team stats table found in {filepath}")
        else:
            raise FileNotFoundError(f"Cache file not found: {filepath.absolute()}")
    except Exception as e:
        st.error(f"Error loading team stats ({stat_type}): {e}")
        return pd.DataFrame()


