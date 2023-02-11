import pandas as pd
import json
import matplotlib.pyplot as plt
import scipy.spatial as sps
import numpy as np
import random

# Load the JSON data from the file
with open("noemoji.json") as file:
    data = json.load(file)

# Extract the "burghs" field from the data
burghs = data["cells"]["burgs"]

# Create a list of dictionaries, where each dictionary represents a row of data for the states
burghs_rows = []
for cell in burghs:
    if isinstance(cell, dict):
        row = {
            "name": cell["name"],
            "x": cell["x"],
            "y": cell["y"],
        }
        burghs_rows.append(row)

# Create data frames from the lists of dictionaries
burghs_df = pd.DataFrame(burghs_rows, columns=["burgh", "x", "y"])

# Filter out rows with x or y outside of specified range
burghs_df = burghs_df[(burghs_df["x"] >= 0) & (burghs_df["x"] <= 10000) &
                      (burghs_df["y"] >= 0) & (burghs_df["y"] <= 10000)]

# Generate a list of points for the Voronoi diagram
points = np.array([[x, y] for x, y in zip(burghs_df["x"], burghs_df["y"])])

# Compute the Voronoi diagram
vor = sps.Voronoi(points)


#plt.plot(points[:, 0], points[:, 1], 'o')


# Plot the Voronoi diagram
fig, ax = plt.subplots(figsize=(8192/300, 4096/300), dpi=300)
plt.xlim(0, 2000)
plt.ylim(0, 2000)
plt.axis('off')
ax.invert_yaxis()

for region in vor.regions:
    if not -1 in region:
        polygon = [vor.vertices[i] for i in region]
        ax.fill(*zip(*polygon), color=np.random.rand(3,))

plt.axis('off')
plt.savefig("voronoi_diagram.png", dpi=300, bbox_inches='tight', pad_inches=0)

