import pandas as pd
import networkx as nx
import numpy as np
import json
import os

def create_synthetic_distance_matrix(locations: list) -> pd.DataFrame:
    """Creates a simulated distance matrix for a list of locations."""
    n = len(locations)
    # Generate symmetric random distances between 1 and 15 km
    dist = np.random.uniform(1, 15, size=(n, n))
    dist = (dist + dist.T) / 2
    np.fill_diagonal(dist, 0)
    
    return pd.DataFrame(dist, index=locations, columns=locations)

def route_dijkstra(prioritized_bins: pd.DataFrame, truck_capacity: int = 20) -> dict:
    """
    Simulates a routing approach to visit high priority bins.
    For the hackathon, we simply cluster by area, pick the top N within capacity.
    Nodes -> areas
    Edges -> distances
    """
    areas = ["Depot"] + prioritized_bins['area'].unique().tolist()
    dist_matrix = create_synthetic_distance_matrix(areas)
    
    G = nx.Graph()
    for i, area in enumerate(areas):
        for j, target in enumerate(areas):
            if i < j:
                G.add_edge(area, target, weight=dist_matrix.loc[area, target])
                
    # Select bins up to truck capacity
    selected_bins = prioritized_bins.head(truck_capacity)
    visited_areas = selected_bins['area'].unique().tolist()
    
    # Build a simple route from Depot -> visiting all visited_areas using a greedy nearest neighbor
    route = ["Depot"]
    current_node = "Depot"
    unvisited = set(visited_areas)
    
    total_distance = 0
    while unvisited:
        # Find nearest neighbor
        distances = {node: G[current_node][node]['weight'] for node in unvisited}
        next_node = min(distances, key=distances.get)
        total_distance += distances[next_node]
        route.append(next_node)
        current_node = next_node
        unvisited.remove(next_node)
        
    # Return to depot
    total_distance += G[current_node]["Depot"]['weight']
    route.append("Depot")
    
    # Calculate load percentage
    load_percentage = (len(selected_bins) / truck_capacity) * 100
    
    result = {
        "route": route,
        "total_distance_km": round(total_distance, 2),
        "bins_collected": len(selected_bins),
        "truck_load_percentage": round(load_percentage, 1),
        "selected_bin_ids": selected_bins['bin_id'].tolist()
    }
    
    os.makedirs("outputs/optimized_routes", exist_ok=True)
    with open("outputs/optimized_routes/waste_routes.json", "w") as f:
        json.dump(result, f, indent=4)
        
    return result

if __name__ == "__main__":
    from waste.routing import calculate_bin_priority, get_high_priority_bins
    from integration.preprocess import load_and_preprocess
    
    df = load_and_preprocess("data/raw/pune_waste_management_dataset_15000_rows.csv")
    df_prio = calculate_bin_priority(df)
    high_prio = get_high_priority_bins(df_prio)
    route = route_dijkstra(high_prio)
    print("Waste Route Summary:")
    print(json.dumps(route, indent=2))
