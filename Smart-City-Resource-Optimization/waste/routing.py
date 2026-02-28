import pandas as pd
import numpy as np

def calculate_bin_priority(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the priority of each bin based on:
    - Fill percentage score (1-10)
    - Overflow risk multiplier
    - Population density weight
    """
    # 1. Fill Level Scoring (0-100% -> 1-10)
    df['fill_score'] = np.ceil(df['fill_percentage'] / 10).clip(lower=1, upper=10)
    
    # 2. Population Weight (normalize population density 5000-20000 -> 0-5)
    pop_min = 5000
    pop_max = 20000
    df['population_weight'] = ((df['population_density'] - pop_min) / (pop_max - pop_min) * 5).clip(lower=0, upper=5)
    
    # 3. Urgency Boost (Formula: priority = fill_score + overflow_risk*2 + population_weight)
    df['priority'] = df['fill_score'] + (df['overflow_risk'] * 2) + df['population_weight']
    
    # Sort by priority descending
    df = df.sort_values(by='priority', ascending=False)
    
    return df

def get_high_priority_bins(df: pd.DataFrame, threshold: float = 12.0) -> pd.DataFrame:
    """Filter bins that need immediate attention."""
    return df[df['priority'] >= threshold].copy()

if __name__ == "__main__":
    from integration.preprocess import load_and_preprocess
    
    df = load_and_preprocess("data/raw/pune_waste_management_dataset_15000_rows.csv", time_col="timestamp")
    df_prioritized = calculate_bin_priority(df)
    high_priority = get_high_priority_bins(df_prioritized)
    
    print(f"Total Bins: {len(df)}")
    print(f"High Priority Bins: {len(high_priority)}")
    print(high_priority.head())
