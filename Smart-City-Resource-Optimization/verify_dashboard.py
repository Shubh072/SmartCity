from src.dashboard.app import get_dashboard_data

print("Testing Dashboard Data Loading...")
data = get_dashboard_data()

print(f"Health Score: {data['health_score']}")
print(f"Waste Priority Length: {len(data['waste']['prio'])}")
print(f"Water Anomalies Length: {len(data['water']['anomalies'])}")
print(f"Disease Alerts Length: {len(data['disease']['alerts'])}")

print("\nRisk Table Head:")
print(data['risk_table'].head())

print("\nSUCCESS! All modules integrated correctly.")
