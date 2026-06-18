import streamlit as st
import folium
import polyline
import requests
from streamlit_folium import st_folium
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
import os

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="India Route Finder", layout="wide")
st.title("🚗 Fast Route Finder (India – OpenRouteService)")

# ----------------------------
# ORS API KEY
# ----------------------------
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ijc5M2Q2ODRiMDFhNDRiYTliMTU1ZGJiOTQ4YWJhZThmIiwiaCI6Im11cm11cjY0In0="

# ----------------------------
# DATASET STORAGE
# ----------------------------
DATA_FILE = "route_dataset.csv"
if os.path.exists(DATA_FILE):
    route_df = pd.read_csv(DATA_FILE)
else:
    route_df = pd.DataFrame(columns=[
        "origin", "destination", "waypoints", "hour", "traffic_level",
        "main_distance_km", "main_time_min",
        "alt_distance_km", "alt_time_min"
    ])

# ----------------------------
# GEOCODING FUNCTION
# ----------------------------
def geocode_place(place):
    url = "https://api.openrouteservice.org/geocode/search"
    params = {"api_key": ORS_API_KEY, "text": place, "size": 1}
    r = requests.get(url, params=params).json()
    try:
        coords = r["features"][0]["geometry"]["coordinates"]
        return coords[1], coords[0]  # lat, lon
    except Exception as e:
        st.error(f"Geocoding failed for '{place}'")
        st.write(r)
        return None, None

# ----------------------------
# ROUTE FUNCTION WITH WAYPOINTS
# ----------------------------
def get_route_with_waypoints(coords_list, traffic_factor):
    ors_coords = [[lon, lat] for lat, lon in coords_list]  # ORS expects [lon, lat]
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    body = {"coordinates": ors_coords}
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}

    try:
        r = requests.post(url, json=body, headers=headers)
        r.raise_for_status()
        data = r.json()
        route = data["routes"][0]
        distance_m = route["summary"]["distance"]
        time_s = route["summary"]["duration"] * traffic_factor
        geometry = route["geometry"]
        route_coords = polyline.decode(geometry)
        return route_coords, distance_m, time_s
    except Exception as e:
        st.error(f"Routing failed: {e}")
        return None, None, None

# ----------------------------
# TRAFFIC BASED ON HOUR
# ----------------------------
def get_hourly_traffic(hour):
    if 6 <= hour < 12:
        return "Medium"
    elif 12 <= hour < 17:
        return "Low"
    elif 17 <= hour < 22:
        return "High"
    else:
        return "Low"

traffic_factor_map = {"Low": 1.0, "Medium": 1.5, "High": 2.2}
current_hour = datetime.now().hour
current_traffic_level = get_hourly_traffic(current_hour)
traffic_factor = traffic_factor_map[current_traffic_level]

st.sidebar.write(f"Current Hour: {current_hour}:00")
st.sidebar.write(f"Traffic Level Based on Time: **{current_traffic_level}**")

# ----------------------------
# SIDEBAR INPUT
# ----------------------------
st.sidebar.header("Enter Locations")
origin = st.sidebar.text_input("From:", "Connaught Place, Delhi")
destination = st.sidebar.text_input("To:", "Indira Gandhi Airport, Delhi")
waypoint_input = st.sidebar.text_input("Waypoints (comma-separated addresses, optional)", "")
st.sidebar.markdown(f"### 🚦 Current Traffic Level: **{current_traffic_level}**")

# Session state for button
if "go_clicked" not in st.session_state:
    st.session_state.go_clicked = False

if st.sidebar.button("Find Route"):
    st.session_state.go_clicked = True

# ----------------------------
# MAIN LOGIC
# ----------------------------
if st.session_state.go_clicked:
    with st.spinner("Geocoding locations..."):
        o_lat, o_lon = geocode_place(origin)
        d_lat, d_lon = geocode_place(destination)

        waypoints = []
        waypoints_str_list = []
        if waypoint_input.strip():
            for wp in waypoint_input.split(","):
                wp_lat, wp_lon = geocode_place(wp.strip())
                if wp_lat is not None:
                    waypoints.append([wp_lat, wp_lon])
                    waypoints_str_list.append(wp.strip())

    if o_lat is None or d_lat is None:
        st.error("❌ Unable to locate one of the places.")
        st.stop()

    coords_list = [[o_lat, o_lon]] + waypoints + [[d_lat, d_lon]]

    with st.spinner("Calculating main route..."):
        main_coords, main_distance, main_time = get_route_with_waypoints(coords_list, traffic_factor)

    if main_coords is None:
        st.error("❌ Main route could not be calculated.")
        st.stop()

    # Simulate alternative route
    alt_coords, alt_distance, alt_time = main_coords[::-1], main_distance*1.1, main_time*1.1

    # ----------------------------
    # DISPLAY MAP
    # ----------------------------
    route_map = folium.Map(location=[o_lat, o_lon], zoom_start=12)
    for i, coord in enumerate(coords_list):
        if i == 0:
            folium.Marker(coord, tooltip="Origin", icon=folium.Icon(color="green")).add_to(route_map)
        elif i == len(coords_list)-1:
            folium.Marker(coord, tooltip="Destination", icon=folium.Icon(color="red")).add_to(route_map)
        else:
            folium.Marker(coord, tooltip=f"Waypoint {i}", icon=folium.Icon(color="blue", icon="flag")).add_to(route_map)

    folium.PolyLine(main_coords, color="red", weight=6, tooltip="Main Route").add_to(route_map)
    folium.PolyLine(alt_coords, color="blue", weight=6, tooltip="Alternative Route").add_to(route_map)
    st_folium(route_map, height=600, width=950)

    # ----------------------------
    # SHOW ROUTE INFO
    # ----------------------------
    st.success("✔ Route Generated Successfully")
    st.write(f"### Main Route: {main_distance/1000:.2f} km, {main_time/60:.1f} min")
    st.write(f"### Alternative Route: {alt_distance/1000:.2f} km, {alt_time/60:.1f} min")

    # ----------------------------
    # ADD GRAPH
    # ----------------------------
    fig = go.Figure(data=[
        go.Bar(name='Distance (km)', x=['Main Route', 'Alternative Route'],
               y=[main_distance/1000, alt_distance/1000]),
        go.Bar(name='Time (min)', x=['Main Route', 'Alternative Route'],
               y=[main_time/60, alt_time/60])
    ])
    fig.update_layout(barmode='group', title="Route Comparison: Distance vs Time")
    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # LOG DATA TO DATASET
    # ----------------------------
    new_row = {
        "origin": origin,
        "destination": destination,
        "waypoints": ";".join(waypoints_str_list),
        "hour": current_hour,
        "traffic_level": current_traffic_level,
        "main_distance_km": main_distance/1000,
        "main_time_min": main_time/60,
        "alt_distance_km": alt_distance/1000,
        "alt_time_min": alt_time/60
    }
    
    route_df = pd.concat([route_df, pd.DataFrame([new_row])], ignore_index=True)
    route_df.to_csv(DATA_FILE, index=False)
    st.success("📊 Route data saved to dataset!")

# ----------------------------
# ANALYSIS TAB
# ----------------------------
st.header("📊 Route Data Analysis")

if route_df.empty:
    st.info("No route data available yet. Run a route first to collect data.")
else:
    # 1️⃣ Show dataset
    st.subheader("Dataset")
    st.dataframe(route_df)

    # 2️⃣ Average main & alternative route times per traffic level
    st.subheader("Average Travel Time per Traffic Level")
    avg_time_df = route_df.groupby("traffic_level")[["main_time_min","alt_time_min"]].mean().reset_index()
    fig1 = go.Figure(data=[
        go.Bar(name="Main Route", x=avg_time_df["traffic_level"], y=avg_time_df["main_time_min"]),
        go.Bar(name="Alternative Route", x=avg_time_df["traffic_level"], y=avg_time_df["alt_time_min"])
    ])
    fig1.update_layout(barmode="group", title="Average Travel Time by Traffic Level (min)")
    st.plotly_chart(fig1, use_container_width=True)

    # 3️⃣ Average distance per traffic level
    st.subheader("Average Distance per Traffic Level")
    avg_dist_df = route_df.groupby("traffic_level")[["main_distance_km","alt_distance_km"]].mean().reset_index()
    fig2 = go.Figure(data=[
        go.Bar(name="Main Route", x=avg_dist_df["traffic_level"], y=avg_dist_df["main_distance_km"]),
        go.Bar(name="Alternative Route", x=avg_dist_df["traffic_level"], y=avg_dist_df["alt_distance_km"])
    ])
    fig2.update_layout(barmode="group", title="Average Distance by Traffic Level (km)")
    st.plotly_chart(fig2, use_container_width=True)

    # 4️⃣ Travel time by hour
    st.subheader("Travel Time by Hour")
    time_hour_df = route_df.groupby("hour")[["main_time_min","alt_time_min"]].mean().reset_index()
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=time_hour_df["hour"], y=time_hour_df["main_time_min"], mode="lines+markers", name="Main Route"))
    fig3.add_trace(go.Scatter(x=time_hour_df["hour"], y=time_hour_df["alt_time_min"], mode="lines+markers", name="Alternative Route"))
    fig3.update_layout(title="Average Travel Time by Hour", xaxis_title="Hour of Day", yaxis_title="Time (min)")
    st.plotly_chart(fig3, use_container_width=True)

    # 5️⃣ Optional: Summary stats
    st.subheader("Summary Statistics")
    st.write(route_df.describe())