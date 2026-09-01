import pandas as pd

def flatten_multiindex_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Aplanar multi-índices de columnas si existen."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join([str(c) for c in col if str(c) != '']).strip() for col in df.columns.values]
    return df

