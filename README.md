# Traffic Route Optimization App 🚦

An intelligent traffic route optimization system built using Python, OSMnx, NetworkX, and Matplotlib.  
The project analyzes road networks, simulates traffic congestion, and finds the most efficient route using Dijkstra’s shortest path algorithm.

## Project Overview

This project compares:

- **Shortest Distance Path**
- **Least Traffic Path**

Instead of considering only road distance, the application also factors in traffic congestion levels to determine the best route.

Example:

Without traffic:
- Path A = 8 km
- Path B = 10 km

With traffic:
- Path A = 8 × 3 = 24 (heavy traffic)
- Path B = 10 × 1 = 10 (light traffic)

➡️ Even though Path B is longer, it becomes the better route due to lower congestion.

---

# Features

- Real-world road network extraction using OpenStreetMap
- Graph-based route modeling
- Dijkstra’s shortest path algorithm
- Traffic-aware path optimization
- Automatic traffic simulation on roads
- Route comparison visualization
- Color-coded traffic routes
- Interactive map plotting using Matplotlib
- Future-ready frontend integration using Streamlit

---

# Technologies Used

## Backend
- Python
- NetworkX
- OSMnx
- Matplotlib
- Random Traffic Simulation

## Frontend (Planned)
- Streamlit
- Tkinter / PyQt

---

# Data Analysis in the Project

## 1. Traffic Pattern Analysis

Traffic values are automatically assigned to roads using simulated congestion levels.

```python
import random

for u, v, k, data in G.edges(keys=True, data=True):
    base_time = data['length'] / 50

    traffic_factor = random.choice([1, 1.5, 2, 3])

    data['traffic_time'] = base_time * traffic_factor
    data['traffic_level'] = traffic_factor
```

Traffic factors:
- 1 → Low traffic
- 1.5 → Medium traffic
- 2 → High traffic
- 3 → Heavy traffic

---

## 2. Path Comparison

The system calculates:

- Shortest path by distance
- Least traffic path

using Dijkstra’s algorithm with different edge weights.

```python
shortest_path = nx.shortest_path(G, orig, dest, weight="length")

least_traffic_path = nx.shortest_path(G, orig, dest, weight="traffic_time")
```

---

## 3. Visualization

Routes are displayed visually on a city map:

- Blue → shortest distance route
- Red → least traffic route

using OSMnx + Matplotlib.

---

# Working Process

1. Download city road network using OSMnx
2. Convert roads into graph structure
3. Assign traffic weights to roads
4. Select source and destination
5. Run Dijkstra’s algorithm
6. Compare optimal routes
7. Visualize results on map

---

# Sample Output

```text
Shortest Path:
Connaught Place → Janpath → India Gate

Distance: 3.2 km
Estimated Time: 12 minutes
Traffic Level: Low
```

---

# Current Setup

Currently the project runs in:
- Spyder IDE
- Matplotlib visualization window

The current map is static.

---

# Future Improvements

- Interactive web frontend using Streamlit
- Real-time traffic integration
- Dynamic route recalculation
- Clickable map interface
- Live traffic heatmaps
- Machine learning-based traffic prediction

---

# Installation

Clone the repository:

```bash
git clone https://github.com/harshitttt21/traffic_route_app.git
```

Move into the project folder:

```bash
cd traffic_route_app
```

Install dependencies:

```bash
pip install osmnx networkx matplotlib
```

Run the application:

```bash
python route_app.py
```

---

# Project Structure

```text
traffic_route_app/
│
├── route_app.py
├── route_dataset.csv
├── cache/
├── README.md
```

# Project Overview

This project analyzes traffic routes and identifies efficient paths using graph-based routing techniques and traffic datasets. The system helps evaluate route efficiency and traffic conditions using Python-based analysis.