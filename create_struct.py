import os

files = [
    "Smart-City-Resource-Optimization/data/raw/water_pipeline_monitoring_dataset_15000_rows.csv",
    "Smart-City-Resource-Optimization/data/raw/pune_waste_management_dataset_15000_rows.csv",
    "Smart-City-Resource-Optimization/data/raw/clean_hospital_dataset_15000_rows.csv",
    "Smart-City-Resource-Optimization/data/processed/water_processed.csv",
    "Smart-City-Resource-Optimization/data/processed/waste_processed.csv",
    "Smart-City-Resource-Optimization/data/processed/hospital_processed.csv",
    "Smart-City-Resource-Optimization/data/external/city_zone_metadata.csv",
    "Smart-City-Resource-Optimization/src/config/config.yaml",
    "Smart-City-Resource-Optimization/src/config/paths.py",
    "Smart-City-Resource-Optimization/src/ingestion/load_water_data.py",
    "Smart-City-Resource-Optimization/src/ingestion/load_waste_data.py",
    "Smart-City-Resource-Optimization/src/ingestion/load_hospital_data.py",
    "Smart-City-Resource-Optimization/src/preprocessing/clean_water_data.py",
    "Smart-City-Resource-Optimization/src/preprocessing/clean_waste_data.py",
    "Smart-City-Resource-Optimization/src/preprocessing/clean_hospital_data.py",
    "Smart-City-Resource-Optimization/src/preprocessing/feature_engineering.py",
    "Smart-City-Resource-Optimization/src/forecasting/water_demand_model.py",
    "Smart-City-Resource-Optimization/src/forecasting/waste_demand_model.py",
    "Smart-City-Resource-Optimization/src/forecasting/hospital_cleaning_demand_model.py",
    "Smart-City-Resource-Optimization/src/forecasting/train_all_models.py",
    "Smart-City-Resource-Optimization/src/graph_model/city_graph.py",
    "Smart-City-Resource-Optimization/src/graph_model/build_graph.py",
    "Smart-City-Resource-Optimization/src/graph_model/graph_utils.py",
    "Smart-City-Resource-Optimization/src/optimization/static_allocation.py",
    "Smart-City-Resource-Optimization/src/optimization/optimized_allocation.py",
    "Smart-City-Resource-Optimization/src/optimization/efficiency_calculator.py",
    "Smart-City-Resource-Optimization/src/routing/dijkstra.py",
    "Smart-City-Resource-Optimization/src/routing/mst.py",
    "Smart-City-Resource-Optimization/src/routing/route_planner.py",
    "Smart-City-Resource-Optimization/src/simulation/simulate_water_supply.py",
    "Smart-City-Resource-Optimization/src/simulation/simulate_waste_collection.py",
    "Smart-City-Resource-Optimization/src/simulation/simulate_cleaning_schedule.py",
    "Smart-City-Resource-Optimization/src/dashboard/app.py",
    "Smart-City-Resource-Optimization/src/dashboard/charts.py",
    "Smart-City-Resource-Optimization/src/dashboard/maps.py",
    "Smart-City-Resource-Optimization/src/dashboard/metrics.py",
    "Smart-City-Resource-Optimization/src/utils/logger.py",
    "Smart-City-Resource-Optimization/src/utils/validators.py",
    "Smart-City-Resource-Optimization/src/utils/helpers.py",
    "Smart-City-Resource-Optimization/models/water_demand_model.pkl",
    "Smart-City-Resource-Optimization/models/waste_demand_model.pkl",
    "Smart-City-Resource-Optimization/models/hospital_cleaning_model.pkl",
    "Smart-City-Resource-Optimization/outputs/predictions/water_predictions.csv",
    "Smart-City-Resource-Optimization/outputs/predictions/waste_predictions.csv",
    "Smart-City-Resource-Optimization/outputs/predictions/hospital_predictions.csv",
    "Smart-City-Resource-Optimization/outputs/optimized_routes/waste_routes.json",
    "Smart-City-Resource-Optimization/outputs/optimized_routes/water_routes.json",
    "Smart-City-Resource-Optimization/outputs/reports/efficiency_report.csv",
    "Smart-City-Resource-Optimization/outputs/reports/comparison_report.pdf",
    "Smart-City-Resource-Optimization/tests/test_forecasting.py",
    "Smart-City-Resource-Optimization/tests/test_graph.py",
    "Smart-City-Resource-Optimization/tests/test_optimization.py",
    "Smart-City-Resource-Optimization/main.py",
    "Smart-City-Resource-Optimization/requirements.txt",
    "Smart-City-Resource-Optimization/README.md"
]

for file_path in files:
    full_path = os.path.join("d:/Users/Windows/Documents/Smartcity", file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        pass

print("Success: Directory structure created.")
