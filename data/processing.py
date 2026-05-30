# data/processing.py
import pandas as pd
from data.model import StravaData


def apply_filter(strava_data: StravaData, column: str, operator: str, value: str, reset: bool) -> bool:
    """Update model condition based on user filter input."""
    if reset:
        strava_data.set_condition(None)
        print('Filter is removed, insert table for default view.')
        return True

    try:
        val = float(value)
    except ValueError:
        print('Value error, please enter valid characters.')
        return False

    col_data = strava_data.data[column]
    if operator == ">":
        condition = col_data > val
    elif operator == "<":
        condition = col_data < val
    elif operator == "<=":
        condition = col_data <= val
    elif operator == ">=":
        condition = col_data >= val
    elif operator == "==":
        condition = col_data == val
    else:
        print('Invalid operation.')
        return False

    print('Filtering is complete!')
    strava_data.set_condition(condition)
    return True


def get_display_data(strava_data: StravaData) -> pd.DataFrame:
    """Sort, filter, and append summable columns for display."""
    df = strava_data.data
    if strava_data.condition is not None:
        df = df[strava_data.condition]
    if strava_data.sort_column is not None:
        df = df.sort_values(by=strava_data.sort_column, ascending=strava_data.sort_ascending)

    return _apply_summable_columns(df.copy())


def _calculate_summable_columns(display_data: pd.DataFrame) -> dict:
    """Calculate aggregate row data."""
    select = ['distance', 'calories', 'average watts']
    sum_dictionary = {}
    dt_columns = display_data.select_dtypes('number').columns

    for i in [col for col in dt_columns if col in select]:
        if i == 'average watts':
            available_watts = display_data[display_data[i].notna()]
            precise_watts = (available_watts[i] * available_watts['moving time/h'] / 1000).sum()
            approx_rides = display_data[display_data[i].isna()]
            approx_watts = (140 * approx_rides['moving time/h'] / 1000).sum()
            kwh = precise_watts + approx_watts
            sum_dictionary[i] = f"{round(kwh, 3)} kWh"
        elif i == 'calories':
            sum_dictionary[i] = f"{round(display_data[i].sum(skipna=True), 3)} Kcal"
        elif i == 'distance':
            sum_dictionary[i] = f"{round(display_data[i].sum(skipna=True), 3)} KMs"

    for j in display_data.columns:
        if j not in sum_dictionary and j == 'activity id':
            sum_dictionary[j] = 'TOTAL:\t'
        elif j not in sum_dictionary:
            sum_dictionary[j] = '**'

    return sum_dictionary


def _apply_summable_columns(display_data: pd.DataFrame) -> pd.DataFrame:
    """Append aggregated dictionary as the bottom row."""
    if display_data.empty:
        return display_data
    sum_dictionary = _calculate_summable_columns(display_data)
    sum_df = pd.DataFrame([sum_dictionary])
    return pd.concat([display_data, sum_df])