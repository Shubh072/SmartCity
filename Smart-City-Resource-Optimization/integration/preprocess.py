import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop NA and duplicate rows."""
    print(f"Original shape: {df.shape}")
    df = df.dropna()
    df = df.drop_duplicates()
    print(f"Cleaned shape: {df.shape}")
    return df

def convert_timestamps(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
    """Convert timestamp column to datetime objects."""
    if time_col in df.columns:
        df[time_col] = pd.to_datetime(df[time_col])
    return df

def encode_categories(df: pd.DataFrame, cat_cols: list) -> pd.DataFrame:
    """Encode categorical columns simply using pandas factorize or dummies.
       For the hackathon, we keep the original string and just ensure it's categorized if needed.
    """
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    return df

def load_and_preprocess(filepath: str, time_col: str=None, cat_cols: list=None) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df = clean_data(df)
    if time_col:
        df = convert_timestamps(df, time_col)
    if cat_cols:
        df = encode_categories(df, cat_cols)
    return df
