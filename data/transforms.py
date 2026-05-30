# data/transforms.py
import pandas as pd

def ms_to_km(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Convert speed from meters per second to kilometers per hour."""
    col = column.lower()
    if col in df.columns:
        df[f"{col} kmh"] = (df[col].astype(float) * 3.6).round(2)
    return df

def secs_to_hour(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Convert speed format to hours."""
    col = column.lower()
    if col in df.columns:
        df[f"{col}/h"] = (df[col] / 3600).round(3)
    return df