import pandas as pd
import json
import random

# Load the JSON data from the file
with open("noemoji.json") as file:
    data = json.load(file)

# Extract the "states" and "provinces" fields from the data
states = data["cells"]["states"]
provinces = data["cells"]["provinces"]
culture = data["cells"]["cultures"]
religions = data["cells"]["religions"]
burgs = data["cells"]["burgs"]

# Create a list of dictionaries, where each dictionary represents a row of data for the states
states_rows = []
for cell in states:
    row = {
        "i": cell["i"],
        "name": cell["name"],
    }
    states_rows.append(row)

# Create a list of dictionaries, where each dictionary represents a row of data for the provinces

provinces_rows = []
suffixes = ["castle", "town", "field", "pool","by","toft","worth","llyn","ay","y","ey","bost","caster","chester","cester","leigh","ley","borough","bury","burgh","wick"]
names_set = set()  # to keep track of unique province names

for cell in provinces:
    if isinstance(cell, dict):
        name = cell["name"]
        base_name = name
        suffix_idx = 1
        while name in names_set:  # check if name is already in set
            name = base_name + suffixes[suffix_idx - 1]  # add a suffix to the name
            suffix_idx += 1
        names_set.add(name)  # add the unique name to the set

        row = {
            "i": cell["i"],
            "state": cell["state"],
            "center": cell["center"],
            "burg": cell["burg"],
            "name": name,
            "formName": cell["formName"],
            "fullName": cell["fullName"],
            "color": cell["color"],
        }
        provinces_rows.append(row)


religions_rows = []
for cell in religions:
    if isinstance(cell, dict):
        origins = cell.get("origins")
        origin = None
        if origins and isinstance(origins, list) and len(origins) > 0:
            origin = origins[0]
        row = {
            "i": cell.get("i"),
            "name": cell.get("name"),
            "type": cell.get("type"),
            "form": cell.get("form"),
            "deity": cell.get("deity"),
            "center": cell.get("center"),
            "origin": origin,
        }
        religions_rows.append(row)



cultures_rows = []
for cell in culture:
    if isinstance(cell, dict):
        row = {
            "i": cell["i"],
            "name": cell["name"],

        }
        cultures_rows.append(row)

suffixes = ["castle", "town", "field", "pool"]
names = set()
burgs_rows = []



suffixes = ["castle", "town", "field", "pool","by","toft","worth","llyn","ay","y","ey","bost","caster","chester","cester","leigh","ley","borough","bury","burgh","wick"]
names = set()
burgs_rows = []

for cell in burgs:
    if isinstance(cell, dict) and cell:
        name = cell.get("name", None)
        suffix = ""
        while name + suffix in names:
            suffix = f"{random.choice(suffixes)}"
            if len(names) >= 4 * len(suffixes) * len(burgs):
                print("ERROR: Could not generate unique names for all burgs.")
                exit()
        names.add(name + suffix)
        row = {
            "i": cell.get("i", None),
            "cell": cell.get("cell", None),
            "name": name + suffix,
        }
        burgs_rows.append(row)


burgs_df = pd.DataFrame(burgs_rows, columns=["i", "cell", "name"])

# Create data frames from the lists of dictionaries
states_df = pd.DataFrame(states_rows, columns=["i", "name"])
provinces_df = pd.DataFrame(provinces_rows, columns=["i", "state", "center", "burg", "name", "formName", "fullName", "color"])
cultures_df = pd.DataFrame(cultures_rows, columns=["i", "name"])
religion_df = pd.DataFrame(religions_rows, columns=["i", "name", "color", "culture", "type", "form", "deity", "center","origin"])
burgs_df = pd.DataFrame(burgs_rows, columns=["i", "cell", "name"])

# Save each data frame to a separate sheet in the same Excel file
with pd.ExcelWriter("combined_data.xlsx") as writer:
    states_df.to_excel(writer, sheet_name="states", index=False)
    provinces_df.to_excel(writer, sheet_name="provinces", index=False)
    cultures_df.to_excel(writer, sheet_name="cultures", index=False)
    religion_df.to_excel(writer, sheet_name="religion", index=False)
    burgs_df.to_excel(writer, sheet_name="burgs", index=False)