import pandas as pd
import numpy as np
import os

from integration.preprocess import load_and_preprocess
from waste.routing import calculate_bin_priority
from water.anomaly_demand import train_leak_detection_model
from disease.trend_alerts import generate_disease_alerts

def load_all_data(base_path: str = ""):
    waste_path = os.path.join(base_path, "data/raw/pune_waste_management_dataset_15000_rows.csv")
    water_path = os.path.join(base_path, "data/raw/water_pipeline_monitoring_dataset_15000_rows.csv")
    disease_path = os.path.join(base_path, "data/raw/clean_hospital_dataset_15000_rows.csv")
    
    waste_df = load_and_preprocess(waste_path)
    water_df = load_and_preprocess(water_path, time_col="timestamp")
    disease_df = load_and_preprocess(disease_path, time_col="date")
    return waste_df, water_df, disease_df

def generate_area_risk_table(waste_df: pd.DataFrame, water_df: pd.DataFrame, disease_df: pd.DataFrame, base_path: str = "") -> pd.DataFrame:
    """
    Fuses risk across the three domains to create a Unified Area Risk Table.
    """
    # 1. Waste Risk (Average Priority per area)
    waste_prio = calculate_bin_priority(waste_df)
    waste_risk = waste_prio.groupby('area')['priority'].mean().reset_index()
    # Normalize 0-100
    w_min = waste_risk['priority'].min()
    w_max = waste_risk['priority'].max()
    waste_risk['waste_risk_score'] = ((waste_risk['priority'] - w_min) / (w_max - w_min + 1e-9) * 100).clip(0, 100)
    
    # 2. Water Risk (Percentage of High Risk anomalies in the last 24 hours per area)
    latest_water = water_df[water_df['timestamp'] >= water_df['timestamp'].max() - pd.Timedelta(days=1)].copy()
    if len(latest_water) > 0:
        latest_water, _ = train_leak_detection_model(latest_water)
        latest_water['is_anomaly'] = (latest_water['leak_risk_level'] == "High Risk").astype(int)
        water_risk = latest_water.groupby('area')['is_anomaly'].mean().reset_index()
        water_risk['water_risk_score'] = (water_risk['is_anomaly'] * 100).clip(0, 100) # Percentage of readings that are anomalies
    else:
        water_risk = pd.DataFrame({'area': waste_risk['area'].unique(), 'water_risk_score': 0})
        
    # 3. Disease Risk (Number of alerts per area)
    alerts = generate_disease_alerts(disease_df)
    if len(alerts) > 0:
        disease_risk = alerts.groupby('area')['is_alert'].sum().reset_index()
        disease_risk['disease_risk_score'] = (disease_risk['is_alert'] * 33.33).clip(0, 100) # Max out quickly
    else:
        disease_risk = pd.DataFrame({'area': waste_risk['area'].unique(), 'disease_risk_score': 0})
        
    # Merge all
    risk_table = pd.merge(pd.DataFrame({'area': waste_risk['area'].unique()}), waste_risk[['area', 'waste_risk_score']], on='area', how='left')
    risk_table = pd.merge(risk_table, water_risk[['area', 'water_risk_score']], on='area', how='left')
    risk_table = pd.merge(risk_table, disease_risk[['area', 'disease_risk_score']], on='area', how='left')
    
    risk_table.fillna(0, inplace=True)
    
    # Final Fusion Logic
    # final_risk = 0.35 * waste + 0.40 * water + 0.25 * disease
    risk_table['final_risk_score'] = (
        0.35 * risk_table['waste_risk_score'] + 
        0.40 * risk_table['water_risk_score'] + 
        0.25 * risk_table['disease_risk_score']
    )
    
    # Generate Cross-Domain Alerts
    cross_alerts = []
    for _, row in risk_table.iterrows():
        alert_msgs = []
        if row['water_risk_score'] > 50 and row['disease_risk_score'] > 30:
            alert_msgs.append("🚨 HEALTH EMERGENCY: Water anomalies coinciding with disease spikes.")
        if row['waste_risk_score'] > 70 and row['disease_risk_score'] > 30:
            alert_msgs.append("🚨 SANITATION ALERT: High waste accumulation and disease spread.")
        if row['water_risk_score'] > 80:
            alert_msgs.append("⚠️ INFRASTRUCTURE ALERT: Severe water pipe anomalies detected.")
            
        cross_alerts.append(" | ".join(alert_msgs) if alert_msgs else "Normal")
        
    risk_table['cross_domain_alert'] = cross_alerts
    risk_table = risk_table.sort_values(by='final_risk_score', ascending=False)
    
    outputs_dir = os.path.join(base_path, "outputs/predictions")
    os.makedirs(outputs_dir, exist_ok=True)
    risk_table.to_csv(os.path.join(outputs_dir, "unified_risk_table.csv"), index=False)
    return risk_table

def get_city_health_score(risk_table: pd.DataFrame) -> float:
    """100 minus average risk."""
    avg_risk = risk_table['final_risk_score'].mean()
    return round(100 - avg_risk, 1)

if __name__ == "__main__":
    waste_df, water_df, disease_df = load_all_data()
    risk_table = generate_area_risk_table(waste_df, water_df, disease_df)
    score = get_city_health_score(risk_table)
    
    print(f"\n🌍 CITY HEALTH SCORE: {score}/100")
    print("\n--- Unified Area Risk Table ---")
    print(risk_table[['area', 'final_risk_score', 'cross_domain_alert']].head())
