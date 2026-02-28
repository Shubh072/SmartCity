import sys
import os

# Robustly get the root of the project which is two directories up from app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Standard imports
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import json

from integration.risk_table import load_all_data, generate_area_risk_table, get_city_health_score
from waste.routing import calculate_bin_priority, get_high_priority_bins
from water.anomaly_demand import analyze_peak_usage, train_leak_detection_model, train_demand_prediction_model
from disease.trend_alerts import aggregate_disease_data, generate_disease_alerts

st.set_page_config(page_title="Smart City Resource Optimization", layout="wide", page_icon="🌍")

# -----------------
# Data Loading
# -----------------
@st.cache_data
def get_dashboard_data():
    waste_df, water_df, disease_df = load_all_data()
    risk_table = generate_area_risk_table(waste_df, water_df, disease_df)
    health_score = get_city_health_score(risk_table)
    
    # Waste Data
    waste_prio = calculate_bin_priority(waste_df)
    high_prio_bins = get_high_priority_bins(waste_prio)
    
    # Try to load route if it exists
    route_data = None
    if os.path.exists("outputs/optimized_routes/waste_routes.json"):
        with open("outputs/optimized_routes/waste_routes.json", "r") as f:
            route_data = json.load(f)
            
    # Water Data
    peaks = analyze_peak_usage(water_df)
    latest_water = water_df[water_df['timestamp'] >= water_df['timestamp'].max() - pd.Timedelta(days=1)].copy()
    latest_water_scored, _ = train_leak_detection_model(latest_water)
    water_anomalies = latest_water_scored[latest_water_scored['leak_risk_level'] == "High Risk"]
    water_demand, _ = train_demand_prediction_model(water_df)
    
    # Disease Data
    disease_alerts = generate_disease_alerts(disease_df)
    weekly_disease = aggregate_disease_data(disease_df)
    
    return {
        "risk_table": risk_table,
        "health_score": health_score,
        "waste": {"prio": waste_prio, "high_prio": high_prio_bins, "route": route_data},
        "water": {"peaks": peaks, "anomalies": water_anomalies, "demand": water_demand},
        "disease": {"alerts": disease_alerts, "weekly": weekly_disease}
    }

data = get_dashboard_data()

# -----------------
# Header Section
# -----------------
st.title("🏙️ Smart City Resource Optimization Brain")
st.markdown("*An AI-powered cross-domain optimization system connecting sanitation, water infrastructure, and public health.*")

# Unified City Health Meter
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=data["health_score"],
    title={'text': "City Health Score"},
    gauge={'axis': {'range': [None, 100]},
           'bar': {'color': "darkblue"},
           'steps': [
               {'range': [0, 40], 'color': "red"},
               {'range': [40, 70], 'color': "yellow"},
               {'range': [70, 100], 'color': "green"}],
        }
))
fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))

col1, col2 = st.columns([1, 2])
with col1:
    st.plotly_chart(fig_gauge, use_container_width=True)
with col2:
    st.subheader("🚨 Active Cross-Domain Alerts")
    critical_alerts = data["risk_table"][data["risk_table"]['cross_domain_alert'] != "Normal"]
    if len(critical_alerts) > 0:
        for _, row in critical_alerts.iterrows():
            st.error(f"**{row['area']}**: {row['cross_domain_alert']}")
    else:
        st.success("No critical cross-domain alerts at this time.")

st.divider()

# -----------------
# Main Tabs
# -----------------
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ City Map", "🚛 Waste Routing", "💧 Water Infrastructure", "🏥 Public Health"])

# Area mapping coordinates (Mock)
area_coords = {
    "Shivajinagar": [18.5314, 73.8446],
    "Kothrud": [18.5074, 73.8077],
    "Hingne Khurd": [18.4831, 73.8219],
    "Wakad": [18.5987, 73.7688],
    "Baner": [18.5590, 73.7868],
    "Viman Nagar": [18.5679, 73.9143],
    "Kalyani Nagar": [18.5471, 73.9033],
    "Koregaon Park": [18.5362, 73.8939]
}

with tab1:
    st.subheader("City Risk Map")
    
    map_data = data["risk_table"].copy()
    map_data['lat'] = map_data['area'].map(lambda x: area_coords.get(x, [0, 0])[0])
    map_data['lon'] = map_data['area'].map(lambda x: area_coords.get(x, [0, 0])[1])
    
    # Simple PyDeck Map
    layer = pdk.Layer(
        "ScatterplotLayer",
        map_data,
        get_position=["lon", "lat"],
        get_color="[255 - final_risk_score, 50, final_risk_score, 200]",
        get_radius="final_risk_score * 30",
        pickable=True
    )
    view_state = pdk.ViewState(latitude=18.5204, longitude=73.8567, zoom=11)
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{area}\nRisk Score: {final_risk_score}"}
    ))
    
    st.dataframe(data["risk_table"].style.background_gradient(cmap="Reds", subset=["final_risk_score"]), use_container_width=True)

with tab2:
    st.subheader("Dynamic Waste Routing")
    st.markdown("**Sensor Choice:** Ultrasonic sensor (HC-SR04) - Cheap, scalable, accurate for non-contact fill-level detection.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total High Priority Bins", len(data["waste"]["high_prio"]))
        st.dataframe(data["waste"]["high_prio"][['bin_id', 'area', 'fill_percentage', 'priority']].head(10))
        
    with col2:
        if data["waste"]["route"]:
            r = data["waste"]["route"]
            st.success("✅ Today's Optimized Route Ready!")
            st.metric("Estimated Distance", f"{r['total_distance_km']} km")
            st.metric("Truck Load %", f"{r['truck_load_percentage']}%")
            st.text("Route Sequence:")
            st.code(" -> ".join(r['route']))
        else:
            st.warning("Run routing script to generate today's route.")

with tab3:
    st.subheader("Water Distribution & Leak Detection")
    st.markdown("**Sensing:** Clamp-on ultrasonic flow meter & Smart quality probes at junctions (no pipe cutting).")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"🛑 **Detected Anomalies (Last 24h):** {len(data['water']['anomalies'])}")
        st.dataframe(data['water']['anomalies'][['sensor_id', 'area', 'pressure_psi', 'flow_rate_lpm', 'turbidity_ntu']])
        
    with col2:
        st.write("📊 **Peak Usage Analysis**")
        fig = px.bar(data['water']['peaks'], x='hour', y='flow_rate_lpm', title="Average Flow Rate by Hour")
        st.plotly_chart(fig, use_container_width=True)
        
    st.write("📈 **Short-term Demand Forecast (System Level)**")
    # Show last 7 days vs forecast
    recent_demand = data['water']['demand'].tail(7)
    fig2 = px.line(recent_demand, x='date', y=['flow_rate_lpm', 'next_day_demand'], 
                   labels={'value': 'Liters per Minute', 'variable': 'Actual vs Predicted'})
    st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.subheader("Local Disease Prevention")
    st.markdown("**Privacy Note:** No personal identifiers used. Analytics are strictly area + disease aggregate counts.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("⚠️ **Hotspot Alerts (Next Week Warning)**")
        alerts = data["disease"]["alerts"]
        active_alerts = alerts[alerts['is_alert'] == True]
        if len(active_alerts) > 0:
            st.dataframe(active_alerts[['area', 'disease', 'growth_rate', 'predicted_next_week']])
        else:
            st.success("No active disease hotspot warnings based on current trend.")
            
    with col2:
        st.write("📉 **Disease Trends by Area**")
        selected_disease = st.selectbox("Select Disease to Plot", ["Dengue", "Malaria", "Diarrhea", "Typhoid", "Cholera"])
        
        filtered = data["disease"]["weekly"][data["disease"]["weekly"]['disease'] == selected_disease]
        fig3 = px.line(filtered, x='week_start', y='cases', color='area', title=f"{selected_disease} Trends")
        st.plotly_chart(fig3, use_container_width=True)
