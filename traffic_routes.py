import osmnx as ox
import networkx as nx
import random
import matplotlib.pyplot as plt

lat, lon = 28.6315, 77.2167
G = ox.graph_from_point((lat, lon), dist=3000, network_type="drive")

sccs = list(nx.strongly_connected_components(G))
largest_scc = max(sccs, key=len)
G = G.subgraph(largest_scc).copy()

print(f"Number of nodes: {G.number_of_nodes()}")
print(f"Number of edges: {G.number_of_edges()}")

for u, v, k, data in G.edges(keys=True, data=True):
    base_time = data['length'] / 50 
    traffic_factor = random.choice([1, 1.5, 2, 3])  
    data['traffic_time'] = base_time * traffic_factor
    data['traffic_level'] = traffic_factor

orig = ox.distance.nearest_nodes(G, 77.2167, 28.6315)  
dest = ox.distance.nearest_nodes(G, 77.2295, 28.6096)  

if nx.has_path(G, orig, dest):
    shortest_path = nx.shortest_path(G, orig, dest, weight="length")
    least_traffic_path = nx.shortest_path(G, orig, dest, weight="traffic_time")

    def path_to_street_names(G, path):
        street_names = []
        for u, v in zip(path[:-1], path[1:]):
            data = G.get_edge_data(u, v)
            name = data[0].get('name', 'Unnamed road')
            street_names.append(name)
        street_names = [street_names[i] for i in range(len(street_names))
                        if i == 0 or street_names[i] != street_names[i-1]]
        return street_names

    shortest_streets = path_to_street_names(G, shortest_path)
    least_traffic_streets = path_to_street_names(G, least_traffic_path)

    print("🚗 Shortest path streets:")
    for i, street in enumerate(shortest_streets, 1):
        print(f"{i}. {street}")

    print("\n🚦 Least traffic path streets:")
    for i, street in enumerate(least_traffic_streets, 1):
        print(f"{i}. {street}")

    fig, ax = ox.plot_graph_routes(
        G,
        routes=[shortest_path, least_traffic_path],
        route_colors=['blue', 'red'],
        route_linewidth=3,
        node_size=0,
        bgcolor="white"
    )
else:
    print("No path exists between the chosen points. Try increasing the graph radius or check coordinates.")