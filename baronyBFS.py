import pandas as pd
from queue import Queue

# Read data from Excel files
combined_data = pd.read_excel("combined_data.xlsx", sheet_name="burgs")
cells_data = pd.read_excel("cellsData.xlsx", usecols=["id", "neighbors", "coordinates", "type"])
cells_data['neighbors'] = cells_data['neighbors'].apply(lambda x: [int(n) for n in x.strip('[]').split(',')])

# Create a dictionary to map cell IDs to town names
id_to_town = dict(zip(combined_data["cell"], combined_data["name"]))

# Define starting points as cells containing towns
start = combined_data["cell"].tolist()

# Define the frontier, cost_so_far, and started_at dictionaries
frontier = Queue()
cost_so_far = dict()
started_at = dict()
coordinates = dict()

# Starting points get distance 0 and will point to themselves
for location in start:
    frontier.put(location)
    cost_so_far[location] = 0
    started_at[location] = location
    coordinates[location] = cells_data.loc[cells_data["id"] == location, "coordinates"].tolist()[0]

# Expand outwards from existing points
while not frontier.empty():
    current = frontier.get()
    if current in cells_data["id"].tolist() and cells_data.loc[cells_data["id"] == current, "type"].tolist()[0] != "ocean":
        for next_cell in cells_data.loc[cells_data["id"] == current, "neighbors"].tolist()[0]:
            if next_cell not in cost_so_far and cells_data.loc[cells_data["id"] == next_cell, "type"].tolist()[0] != "ocean":
                cost_so_far[next_cell] = cost_so_far[current] + 1
                started_at[next_cell] = started_at[current]
                coordinates[next_cell] = cells_data.loc[cells_data["id"] == next_cell, "coordinates"].tolist()[0]
                frontier.put(next_cell)

# Create a DataFrame to store the results
output_data = pd.DataFrame(list(cost_so_far.items()), columns=["id", "distance"])

# Add a column to the output DataFrame for the nearest town and coordinates
output_data["nearest_town"] = output_data["id"].apply(lambda x: id_to_town[started_at[x]])
output_data["coordinates"] = output_data["id"].apply(lambda x: coordinates.get(x))

# Save the output DataFrame to a new Excel file
output_data.to_excel("BFSoutput.xlsx", index=False)
