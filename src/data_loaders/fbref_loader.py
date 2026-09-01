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

@st.cache_data(show_spinner=False, ttl=43200, max_entries=1)
def load_player_season_stats(league, season):
    try:
        from pathlib import Path
        from lxml import html as lxml_html
        import io

        base_dir = Path(__file__).parent.parent.parent
        cache_dir = base_dir / "soccerdata_cache"

        # FBref file pattern
        filemask = f"players_{league}_{season}_{{}}.html"
        
        def parse_table(stat_type):
            filepath = cache_dir / filemask.format(stat_type)
            if not filepath.exists():
                return pd.DataFrame()
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    tree = lxml_html.parse(f)
                for comment in tree.xpath("//comment()"):
                    if f"div_stats_{stat_type}" in comment.text:
                        df = pd.read_html(io.StringIO(comment.text), header=[0, 1])[0]
                        # Flatten columns
                        df.columns = ["_".join([str(x) for x in col if str(x) != "" and "Unnamed" not in str(x)]).strip() for col in df.columns.values]
                        df = df.reset_index(drop=True)
                        if "Player" in df.columns:
                            df = df[df["Player"] != "Player"].reset_index(drop=True)
                        return df
            except Exception:
                pass
            return pd.DataFrame()

        # Parse standard stats (always expected)
        df_std = parse_table("standard")
        if df_std.empty:
            return pd.DataFrame()

        # Parse advanced stats if available
        df_def = parse_table("defense")
        df_pos = parse_table("possession")
        df_pas = parse_table("passing")

        # Merge them on base columns
        merge_cols = ["Player", "Nation", "Pos", "Squad", "Age", "Born"]
        df_final = df_std.copy()
        
        for df_extra in [df_def, df_pos, df_pas]:
            if not df_extra.empty:
                # keep only merge cols + new cols to avoid duplicates
                new_cols = [c for c in df_extra.columns if c not in df_final.columns or c in merge_cols]
                df_final = pd.merge(df_final, df_extra[new_cols], on=merge_cols, how="left")

        return df_final
    except Exception as e:
        st.error(f"Error loading FBref player stats: {e}")
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
