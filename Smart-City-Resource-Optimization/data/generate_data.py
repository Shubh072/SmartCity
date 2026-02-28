import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_waste_data(num_rows=15000, output_path="data/raw/pune_waste_management_dataset_15000_rows.csv"):
    np.random.seed(42)
    areas = ["Shivajinagar", "Kothrud", "Hingne Khurd", "Wakad", "Baner", "Viman Nagar", "Kalyani Nagar", "Koregaon Park"]
    
    data = {
        "bin_id": [f"BIN_{i:04d}" for i in range(num_rows)],
        "area": np.random.choice(areas, num_rows),
        "fill_percentage": np.random.uniform(0, 100, num_rows),
        "overflow_risk": np.random.choice([0, 1], p=[0.8, 0.2], size=num_rows), # 1 if high risk
        "population_density": np.random.uniform(5000, 20000, num_rows), # people per sq km in that area
        "timestamp": [(datetime.now() - timedelta(minutes=np.random.randint(0, 1440))).strftime("%Y-%m-%d %H:%M:%S") for _ in range(num_rows)]
    }
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_rows} rows for Waste Management.")

def generate_water_data(num_rows=15000, output_path="data/raw/water_pipeline_monitoring_dataset_15000_rows.csv"):
    np.random.seed(42)
    areas = ["Shivajinagar", "Kothrud", "Hingne Khurd", "Wakad", "Baner", "Viman Nagar", "Kalyani Nagar", "Koregaon Park"]
    
    # Generate continuous timestamp for 30 days
    base_time = datetime.now() - timedelta(days=30)
    timestamps = [base_time + timedelta(hours=i) for i in range(num_rows)]
    
    # Features for Isolation Forest
    pressure = np.random.normal(50, 5, num_rows) # Normal pressure ~50 psi
    flow_rate = np.random.normal(100, 15, num_rows)
    turbidity = np.random.uniform(0.5, 5.0, num_rows)
    chlorine = np.random.uniform(0.2, 2.0, num_rows)
    pH = np.random.normal(7.2, 0.3, num_rows)
    
    # Introduce anomalies
    anomaly_indices = np.random.choice(num_rows, int(num_rows * 0.05), replace=False)
    pressure[anomaly_indices] -= np.random.uniform(10, 30, len(anomaly_indices)) # Drops pressure
    flow_rate[anomaly_indices] += np.random.uniform(20, 50, len(anomaly_indices)) # Spike in flow (leak)
    turbidity[anomaly_indices] += np.random.uniform(5, 15, len(anomaly_indices)) # Dirty water
    
    data = {
        "sensor_id": [f"W_SENS_{i%100:03d}" for i in range(num_rows)],
        "area": np.random.choice(areas, num_rows),
        "timestamp": [t.strftime("%Y-%m-%d %H:%M:%S") for t in timestamps],
        "pressure_psi": pressure,
        "flow_rate_lpm": flow_rate,
        "turbidity_ntu": turbidity,
        "chlorine_mgl": chlorine,
        "pH": pH,
        "is_leak_simulated": [1 if i in anomaly_indices else 0 for i in range(num_rows)]
    }
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_rows} rows for Water Pipeline.")

def generate_disease_data(num_rows=15000, output_path="data/raw/clean_hospital_dataset_15000_rows.csv"):
    np.random.seed(42)
    areas = ["Shivajinagar", "Kothrud", "Hingne Khurd", "Wakad", "Baner", "Viman Nagar", "Kalyani Nagar", "Koregaon Park"]
    diseases = ["Dengue", "Malaria", "Diarrhea", "Typhoid", "Cholera"]
    
    base_time = datetime.now() - timedelta(days=90)
    
    data = {
        "record_id": [f"REC_{i:05d}" for i in range(num_rows)],
        "area": np.random.choice(areas, num_rows),
        "disease": np.random.choice(diseases, num_rows, p=[0.3, 0.1, 0.4, 0.1, 0.1]),
        "date": [(base_time + timedelta(days=np.random.randint(0, 90))).strftime("%Y-%m-%d") for _ in range(num_rows)],
        "cases": np.random.poisson(lam=3, size=num_rows)
    }
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_rows} rows for Hospital/Disease Dataset.")

if __name__ == "__main__":
    generate_waste_data()
    generate_water_data()
    generate_disease_data()
    print("All synthetic data generated successfully.")
