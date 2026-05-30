# data/loader.py
import pandas as pd
import pathlib as pl
from tkinter import filedialog
from data.transforms import ms_to_km, secs_to_hour
from data.model import StravaData
import config


def load_csv_data() -> StravaData:
    """Open a .csv file, apply transforms, and return a StravaData instance."""
    path = filedialog.askopenfilename()
    if not path:
        return None

    try:
        df = pd.read_csv(pl.Path(path))
    except Exception as e:
        raise IOError(f"Failed to read CSV: {e}") from e

    df.columns = [c.lower() for c in df.columns]

    if 'activity date' in df.columns:
        df['activity date'] = pd.to_datetime(df['activity date'], format="%b %d, %Y, %I:%M:%S %p")

    # Apply Transformations
    df = ms_to_km(df, 'average speed')
    df = ms_to_km(df, 'max speed')
    df = secs_to_hour(df, 'moving time')

    # Filter configured items
    valid_cols = [item for item in config.DEFAULT_COLUMNS if item in df.columns]
    df = df[valid_cols]

    return StravaData(df)