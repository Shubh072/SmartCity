import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle
import os

def analyze_peak_usage(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze peak water usage times by grouping by hour."""
    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
    df['hour'] = df['timestamp'].dt.hour
    peak_usage = df.groupby('hour')['flow_rate_lpm'].mean().reset_index()
    return peak_usage

def train_leak_detection_model(df: pd.DataFrame, model_path="models/water_anomaly_model.pkl", base_path=""):
    """
    Train an Isolation Forest for leak detection based on pressure, flow rate, and quality.
    Features: pressure_psi, flow_rate_lpm, turbidity_ntu, chlorine_mgl, pH
    """
    full_model_path = os.path.join(base_path, model_path)
    features = ['pressure_psi', 'flow_rate_lpm', 'turbidity_ntu', 'chlorine_mgl', 'pH']
    X = df[features].copy()
    
    # Fill NAs if any
    X = X.fillna(X.median())
    
    # Train model
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    
    os.makedirs(os.path.dirname(full_model_path), exist_ok=True)
    with open(full_model_path, "wb") as f:
        pickle.dump(model, f)
        
    # Generate scores
    df['anomaly_score'] = model.decision_function(X)
    df['leak_risk_level'] = model.predict(X)  # -1 for anomaly, 1 for normal
    df['leak_risk_level'] = df['leak_risk_level'].apply(lambda x: "High Risk" if x == -1 else "Normal")
    
    return df, model

def train_demand_prediction_model(df: pd.DataFrame, model_path="models/water_demand_model.pkl", base_path=""):
    """
    Train a simple Linear Regression to predict next day demand.
    """
    full_model_path = os.path.join(base_path, model_path)
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
    # Group by date
    df['date'] = df['timestamp'].dt.date
    daily_demand = df.groupby('date')['flow_rate_lpm'].sum().reset_index()
    daily_demand['next_day_demand'] = daily_demand['flow_rate_lpm'].shift(-1)
    
    # Drop last row which will be NA
    daily_demand = daily_demand.dropna()
    
    X = daily_demand[['flow_rate_lpm']]
    y = daily_demand['next_day_demand']
    
    if len(X) < 2:
        return daily_demand, None
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    os.makedirs(os.path.dirname(full_model_path), exist_ok=True)
    with open(full_model_path, "wb") as f:
        pickle.dump(model, f)
    
    return daily_demand, model

if __name__ == "__main__":
    from src.ingestion.preprocess import load_and_preprocess
    
    df = load_and_preprocess("data/raw/water_pipeline_monitoring_dataset_15000_rows.csv", time_col="timestamp")
    
    # 1. Peak Usage
    peaks = analyze_peak_usage(df)
    print("\n--- Peak Usage ---")
    print(peaks.sort_values(by='flow_rate_lpm', ascending=False).head())
    
    # 2. Leak Detection
    df_anomaly, iso_model = train_leak_detection_model(df)
    anomalies = df_anomaly[df_anomaly['leak_risk_level'] == "High Risk"]
    print(f"\n--- Leak Model ---")
    print(f"Total Anomalies Detected: {len(anomalies)}")
    
    # 3. Demand Prediction
    daily, lr_model = train_demand_prediction_model(df)
    if lr_model:
        print("\n--- Demand Prediction ---")
        print(f"Model R^2: {lr_model.score(daily[['flow_rate_lpm']], daily['next_day_demand']):.4f}")
