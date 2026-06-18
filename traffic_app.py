import streamlit as st
import osmnx as ox
import networkx as nx
import random
import matplotlib.pyplot as plt

st.set_page_config(page_title="Delhi Route Finder", layout="wide")
st.title("🚗 Delhi Route Finder with Traffic Simulation")

# Input location and distance
lat = st.number_input("Enter latitude:", value=28.6315)
lon = st.number_input("Enter longitude:", value=77.2167)
dist = st.slider("Search radius (meters):", 1000, 5000, 3000)

if st.button("Generate Routes"):
    with st.spinner("Building road network..."):
        G = ox.graph_from_point((lat, lon), dist=dist, network_type="drive")

        # Keep the largest connected subgraph
        sccs = list(nx.strongly_connected_components(G))
        largest_scc = max(sccs, key=len)
        G = G.subgraph(largest_scc).copy()

        # Add traffic weights
        for u, v, k, data in G.edges(keys=True, data=True):
            base_time = data['length'] / 50  
            traffic_factor = random.choice([1, 1.5, 2, 3])  
            data['traffic_time'] = base_time * traffic_factor
            data['traffic_level'] = traffic_factor

        orig = ox.distance.nearest_nodes(G, X=lon, Y=lat)
        dest = ox.distance.nearest_nodes(G, X=lon + 0.01, Y=lat - 0.01)

        if nx.has_path(G, orig, dest):
            shortest_path = nx.shortest_path(G, orig, dest, weight="length")
            least_traffic_path = nx.shortest_path(G, orig, dest, weight="traffic_time")

            fig, ax = ox.plot_graph_routes(
                G,
                routes=[shortest_path, least_traffic_path],
                route_colors=['blue', 'red'],
                route_linewidth=3,
                node_size=0,
                bgcolor="white",
                show=False,
                close=False
            )
            st.pyplot(fig)

            st.success("✅ Map Generated Below")

        else:
            st.error("No path exists between the chosen points.")