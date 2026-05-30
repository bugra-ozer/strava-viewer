# data/model.py
import pandas as pd

class StravaData:
    """Manages the underlying DataFrame and sort/filter states."""
    def __init__(self, df: pd.DataFrame):
        self.data = df.copy()
        self.condition = None
        self.sort_column = None
        self.sort_ascending = True

    def set_sort(self, column: str):
        """Toggle sort direction or change sort column."""
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_ascending = True
        self.sort_column = column

    def set_condition(self, condition):
        """Set boolean mask for filtering."""
        self.condition = condition