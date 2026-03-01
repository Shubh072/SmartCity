import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import pickle
import os

def aggregate_disease_data(df: pd.DataFrame) -> pd.DataFrame:
    """Group by area, disease, and week to get counts."""
    # Ensure date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.dayofweek, unit='d')
    
    weekly = df.groupby(['area', 'disease', 'week_start'])['cases'].sum().reset_index()
    weekly = weekly.sort_values(by=['area', 'disease', 'week_start'])
    return weekly

def train_disease_trend_model(df: pd.DataFrame, model_path="models/disease_trend_model.pkl", base_path=""):
    """
    Train a simple Linear Regression model for trend prediction.
    Features: lag_1_week, lag_2_week
    """
    full_model_path = os.path.join(base_path, model_path)
    weekly = aggregate_disease_data(df)
    
    # Create lag features
    weekly['cases_lag_1'] = weekly.groupby(['area', 'disease'])['cases'].shift(1)
    weekly['cases_lag_2'] = weekly.groupby(['area', 'disease'])['cases'].shift(2)
    
    # Drop NAs
    model_df = weekly.dropna()
    
    X = model_df[['cases_lag_1', 'cases_lag_2']]
    y = model_df['cases']
    
    if len(X) < 2:
        return weekly, None
        
    model = LinearRegression()
    model.fit(X, y)
    
    os.makedirs(os.path.dirname(full_model_path), exist_ok=True)
    with open(full_model_path, "wb") as f:
        pickle.dump(model, f)
        
    return weekly, model

def generate_disease_alerts(df: pd.DataFrame, threshold: int = 15, growth_rate_threshold: float = 1.2):
    """
    Alert Rule: If predicted_cases > threshold AND growth_rate > X -> alert
    For simplicity, we use the latest week's data to calculate current growth rate.
    """
    weekly = aggregate_disease_data(df)
    
    # Get latest two weeks per area-disease
    latest = weekly.groupby(['area', 'disease']).tail(2)
    
    alerts = []
    
    for (area, disease), group in latest.groupby(['area', 'disease']):
        if len(group) == 2:
            prev_cases = group.iloc[0]['cases']
            curr_cases = group.iloc[1]['cases']
            
            # Simple prediction: moving average + momentum
            if prev_cases == 0:
                growth_rate = 1.0
            else:
                growth_rate = curr_cases / prev_cases
                
            predicted_next = curr_cases * growth_rate
            
            is_alert = (predicted_next > threshold) and (growth_rate > growth_rate_threshold)
            
            alerts.append({
                'area': area,
                'disease': disease,
                'current_cases': curr_cases,
                'growth_rate': round(growth_rate, 2),
                'predicted_next_week': round(predicted_next, 2),
                'is_alert': is_alert
            })
            
    alerts_df = pd.DataFrame(alerts)
    return alerts_df

if __name__ == "__main__":
    from src.ingestion.preprocess import load_and_preprocess
    
    df = load_and_preprocess("data/raw/clean_hospital_dataset_15000_rows.csv", time_col="date")
    
    weekly, _ = train_disease_trend_model(df)
    print("\n--- Weekly Aggregation ---")
    print(weekly.head())
    
    alerts = generate_disease_alerts(df)
    print("\n--- Disease Alerts ---")
    print(alerts[alerts['is_alert'] == True].head())
