import pandas as pd


def remove_empty_first_rows(table: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Analog process to detect_headers for csv files, determines how many rows to skip
    to end up with the header at the right place"""
    idx = 0
    if all([str(c).startswith('Unnamed:') for c in table.columns]):
        # there is on offset between the index in the file (idx here)
        # and the index in the dataframe, because of the header
        idx = 1
        while table.iloc[idx - 1].isna().all():
            idx += 1
        cols = table.iloc[idx - 1]
        table = table.iloc[idx:]
        table.columns = cols.to_list()
    # +1 here because the headers should count as a row
    return table, idx
