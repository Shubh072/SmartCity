import sys
import os

# Robustly get the root of the project which is one directory up from app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
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
from integration.notifier import send_emergency_sms, send_emergency_email

# Area mapping coordinates (Mock)
AREA_COORDS = {
    "Shivajinagar": [18.5314, 73.8446],
    "Kothrud": [18.5074, 73.8077],
    "Hingne Khurd": [18.4831, 73.8219],
    "Wakad": [18.5987, 73.7688],
    "Baner": [18.5590, 73.7868],
    "Viman Nagar": [18.5679, 73.9143],
    "Kalyani Nagar": [18.5471, 73.9033],
    "Koregaon Park": [18.5362, 73.8939]
}

st.set_page_config(page_title="Smart City Resource Optimization", layout="wide", page_icon="🌍")

# -----------------
# Authentication & RBAC
# -----------------
USER_ROLES = {
    "superadmin": {"pass": "super123", "role": "Super Admin"},
    "admin": {"pass": "admin123", "role": "Admin"},
    "user": {"pass": "user123", "role": "Citizen"}
}

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['role'] = None

def login_form():
    st.title("🔐 Smart City Brain Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username in USER_ROLES and USER_ROLES[username]["pass"] == password:
                st.session_state['authenticated'] = True
                st.session_state['role'] = USER_ROLES[username]["role"]
                st.success(f"Logged in as {st.session_state['role']}")
                st.rerun()
            else:
                st.error("Invalid credentials.")
    
    st.info("Demo Accounts:\n- superadmin / super123\n- admin / admin123\n- user / user123")
    st.stop()

if not st.session_state['authenticated']:
    login_form()

# -----------------
# App Logout & Info
# -----------------
with st.sidebar:
    st.markdown(f"👤 **Logged in as:** {st.session_state['role']}")
    if st.button("🚪 Logout"):
        st.session_state['authenticated'] = False
        st.session_state['role'] = None
        st.rerun()
    st.divider()


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
# Citizen Simulation & Awareness Sidebar
# -----------------
with st.sidebar:
    st.header("📲 Citizen App")
    
    # 1. Action: Reporting
    st.subheader("Report Issue")
    if st.button("🚨 Report Overflowing Bin in Baner", use_container_width=True):
        st.session_state['citizen_report_baner'] = True
        st.success("Report received!")
    if st.button("🔄 Reset Reports", use_container_width=True):
        st.session_state['citizen_report_baner'] = False
        st.rerun()
    
    st.divider()
    
    # 2. Awareness: Personal Impact Calculator
    st.subheader("🌱 My Impact Calculator")
    st.caption("Calculate your contribution to CO2 reduction.")
    paper = st.number_input("Paper recycled (kg)", min_value=0.0, value=0.0, step=0.5)
    plastic = st.number_input("Plastic recycled (kg)", min_value=0.0, value=0.0, step=0.5)
    
    # Simple conversion: 1kg paper ~ 1.5kg CO2 saved, 1kg plastic ~ 2.5kg CO2 saved
    personal_co2_saved = (paper * 1.5) + (plastic * 2.5)
    st.metric("My CO2 Saved", f"{personal_co2_saved:.1f} kg")
    
    st.divider()
    
    # 3. Education: Segregation Guide
    with st.expander("♻️ Waste Segregation Guide"):
        st.markdown("""
        **🟢 Wet Waste (Biodegradable):** Food scraps, fruit peels, flowers.
        **🔵 Dry Waste (Recyclable):** Paper, plastic, metal, dry glass.
        **🔴 Domestic Hazardous:** Batteries, cleaning agents, paint.
        **🟡 E-Waste:** Cables, mobile parts, old batteries.
        """)

# Inject Citizen Data
if st.session_state.get('citizen_report_baner', False):
    mock_bin = pd.DataFrame([{
        'bin_id': 'BIN-CITIZEN-999',
        'area': 'Baner',
        'fill_percentage': 100.0,
        'overflow_risk': 1,
        'population_density': 8000,
        'timestamp': pd.Timestamp.now(),
        'priority': 99.9
    }])
    data["waste"]["high_prio"] = pd.concat([mock_bin, data["waste"]["high_prio"]], ignore_index=True)
    data["risk_table"].loc[data["risk_table"]['area'] == 'Baner', 'final_risk_score'] = 95.0
    data["risk_table"].loc[data["risk_table"]['area'] == 'Baner', 'cross_domain_alert'] = "🚨 CITIZEN REPORT: Overflowing Waste Emergency"


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
    if st.session_state['role'] in ["Super Admin", "Admin"]:
        st.subheader("🚨 Active Cross-Domain Alerts")
        critical_alerts = data["risk_table"][data["risk_table"]['cross_domain_alert'] != "Normal"]
        if len(critical_alerts) > 0:
            for _, row in critical_alerts.iterrows():
                st.error(f"**{row['area']}**: {row['cross_domain_alert']}")
                
            if st.session_state['role'] == "Super Admin":
                st.markdown("---")
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("📱 Dispatch Emergency SMS", use_container_width=True):
                        top_alert = critical_alerts.iloc[0]
                        msg = f"SMART CITY ALERT ({top_alert['area']}): {top_alert['cross_domain_alert']}"
                        with st.spinner("Dispatching via Twilio..."):
                            success = send_emergency_sms(msg)
                            if success:
                                st.success("✅ SMS Alert Dispatched Successfully!")
                            else:
                                st.error("❌ Failed to send SMS. Check your credentials in .env.")
                                
                with col_btn2:
                    if st.button("📧 Dispatch Emergency Email", use_container_width=True):
                        top_alert = critical_alerts.iloc[0]
                        msg = f"SMART CITY ALERT ({top_alert['area']}): {top_alert['cross_domain_alert']}"
                        with st.spinner("Dispatching via SMTP..."):
                            success = send_emergency_email(msg, subject=f"🚨 EMERGENCY: {top_alert['area']}")
                            if success:
                                st.success("✅ Email Alert Dispatched Successfully!")
                            else:
                                st.error("❌ Failed to send Email. Check your credentials in .env.")
        else:
            st.success("No critical cross-domain alerts at this time.")
    else:
        st.subheader("ℹ️ Citizen Information")
        st.info("The city monitoring system is currently active. For emergencies, please call 112 or use the reporting tool in the sidebar.")


st.divider()

# -----------------
# AI Executive Summary
# -----------------
st.subheader("🤖 AI City Manager Narrative")
critical_alerts_updated = data["risk_table"][data["risk_table"]['cross_domain_alert'] != "Normal"]

if data["health_score"] > 85 and len(critical_alerts_updated) == 0:
    summary = "**AI Assessment**: City infrastructure is operating at optimal efficiency. Resource allocation is balanced, and no critical anomalies are detected."
elif len(critical_alerts_updated) > 0:
    areas = ", ".join(critical_alerts_updated['area'].tolist())
    summary = f"**AI Assessment**: Critical infrastructure intervention required in **{areas}** today. Cross-domain risk factors or citizen reports detected. Dispatching targeted emergency maintenance crews is highly recommended."
else:
    high_water = len(data['water']['anomalies'])
    high_bins = len(data['waste']['high_prio'])
    summary = f"**AI Assessment**: City health is moderately stable. Currently tracking {high_water} water pressure anomalies and {high_bins} priority waste bins for optimized routing. No immediate multi-domain emergencies."

st.info(summary)

st.divider()

# -----------------
# Main Tabs
# -----------------
# Main Tabs
# -----------------
tabs_list = ["🗺️ City Map", "🏥 Public Health", "🏆 Leaderboard"]
if st.session_state['role'] in ["Super Admin", "Admin"]:
    tabs_list.extend(["🚛 Waste Routing", "💧 Water Infrastructure"])
if st.session_state['role'] == "Super Admin":
    tabs_list.append("💰 City CFO (ROI)")

tabs = st.tabs(tabs_list)

# Map tab is always first index if citizen, but we need to track index correctly
# A better way is to check the tab names in the loop
for i, tab_name in enumerate(tabs_list):
    with tabs[i]:
        if "City Map" in tab_name:
            st.subheader("City Risk Map")
            
            map_data = data["risk_table"].copy()
            map_data['lat'] = map_data['area'].map(lambda x: AREA_COORDS.get(x, [0, 0])[0])
            map_data['lon'] = map_data['area'].map(lambda x: AREA_COORDS.get(x, [0, 0])[1])
            
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

        elif "Waste Routing" in tab_name:
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

        elif "Water Infrastructure" in tab_name:
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

        elif "Public Health" in tab_name:
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

        elif "Leaderboard" in tab_name:
            st.subheader("Community Green Leaderboard")
            st.markdown("Ranking city areas based on waste management and infrastructure health.")
            
            # Create a mock leaderboard based on risk scores (lower risk = better rank)
            leaderboard_df = data["risk_table"][['area', 'final_risk_score']].copy()
            leaderboard_df['cleanliness_score'] = 100 - leaderboard_df['final_risk_score']
            leaderboard_df = leaderboard_df.sort_values('cleanliness_score', ascending=False).reset_index(drop=True)
            leaderboard_df.index += 1
            
            # Highlight top area
            top_area = leaderboard_df.iloc[0]['area']
            st.success(f"🏆 **{top_area}** is currently the cleanest area in the city!")
            
            # Display table with medals
            leaderboard_df['Rank'] = leaderboard_df.index.map(lambda x: f"🥇 {x}" if x==1 else (f"🥈 {x}" if x==2 else (f"🥉 {x}" if x==3 else str(x))))
            st.table(leaderboard_df[['Rank', 'area', 'cleanliness_score']].rename(columns={'area': 'Neighborhood', 'cleanliness_score': 'Eco Score'}))


        elif "City CFO (ROI)" in tab_name:
            st.subheader("City CFO: ROI & Environmental Impact")
            st.markdown("Real-time calculation of savings generated by AI optimization vs. traditional operations.")
            
            col1, col2, col3 = st.columns(3)
            
            # 1. Fuel Savings (Assuming 2km driven per bin normally)
            standard_route_km = len(data["waste"]["prio"]) * 2 
            if data["waste"]["route"]:
                optimized_km = data["waste"]["route"]['total_distance_km']
            else:
                optimized_km = len(data["waste"]["high_prio"]) * 1.5
                
            km_saved = max(0, standard_route_km - optimized_km)
            diesel_saved_liters = km_saved / 4.0 # Assumed truck mileage 4 km/l
            money_saved_rs = diesel_saved_liters * 90 # 90 Rs/liter
            
            with col1:
                st.metric(label="🚚 Daily Fleet Fuel Savings", value=f"₹ {money_saved_rs:,.0f}", delta=f"{diesel_saved_liters:,.1f} L Diesel Saved")
                st.write(f"Avoided {km_saved:,.0f} km of unoptimized driving.")
                
            # 2. Water Saved (Assuming 1 leak = 24k L/day lost, 0.02 Rs/L processing cost)
            leaks_prevented = len(data['water']['anomalies'])
            liters_saved = leaks_prevented * 24000 
            water_money_saved = liters_saved * 0.02 
            
            with col2:
                st.metric(label="💧 Prevented Water Loss", value=f"₹ {water_money_saved:,.0f}", delta=f"{liters_saved:,.0f} Liters Retained")
                st.write(f"Early detection of {leaks_prevented} pipeline anomalies.")
                
            # 3. Carbon/ESG (2.68 kg CO2 per liter of diesel)
            co2_saved = diesel_saved_liters * 2.68
            
            with col3:
                st.metric(label="🌲 Carbon Footprint Reduction", value=f"{co2_saved:,.1f} kg CO2", delta="ESG Boost")
                st.write("Emissions prevented via AI routing.")
                
            st.divider()
            st.markdown("### Total Projected Annual Savings")
            annual_savings = (money_saved_rs + water_money_saved) * 365
            st.success(f"## ₹ {annual_savings:,.0f} / year")
            st.caption("Based on extrapolating today's AI optimization metrics across a 365-day operational window.")
