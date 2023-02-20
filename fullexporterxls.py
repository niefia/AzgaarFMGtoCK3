import pandas as pd
import json

# Load the JSON data from the file
with open("noemoji.json") as file:
    data = json.load(file)

# Extract the "states" and "provinces" fields from the data
states = data["cells"]["states"]
provinces = data["cells"]["provinces"]
culture = data["cells"]["cultures"]
religions = data["cells"]["religions"]
burgs = data["cells"]["burgs"]
cells = data["cells"]["cells"]

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
for cell in provinces:
    if isinstance(cell, dict):
        row = {
            "i": cell["i"],
            "state": cell["state"],
            "center": cell["center"],
            "burg": cell["burg"],
            "name": cell["name"],
            "formName": cell["formName"],
            "fullName": cell["fullName"],
            "color": cell["color"],
        }
        provinces_rows.append(row)

# Create a list of dictionaries, where each dictionary represents a row of data for the religions
religions_rows = []
for cell in religions:
    if isinstance(cell, dict):
        row = {
            "i": cell["i"],
            "name": cell["name"],


        }
        religions_rows.append(row)

# Create a list of dictionaries, where each dictionary represents a row of data for the cultures
cultures_rows = []
for cell in culture:
    if isinstance(cell, dict):
        row = {
            "i": cell["i"],
            "name": cell["name"],

        }
        cultures_rows.append(row)


# Create a list of dictionaries, where each dictionary represents a row of data for the burgs
burgs_rows = []
for cell in burgs:
    if isinstance(cell, dict) and cell:
        row = {
            "i": cell.get("i", None),
            "cell": cell.get("cell", None),
            "x": cell.get("x", None),
            "y": cell.get("y", None),
            "name": cell.get("name", None),
        }
        burgs_rows.append(row)

# Create a list of dictionaries, where each dictionary represents a row of data for the cells

cells_rows = []
for cell in cells:
    if isinstance(cell, dict):
        row = {
            "i": cell["i"],
            "v": cell["v"],
            "c": cell["c"],
            "p": cell["p"],
            "g": cell["g"],
            "h": cell["h"],
            "area": cell["area"],
            "f": cell["f"],
            "t": cell["t"],
            "haven": cell["haven"],
            "harbor": cell["harbor"],
            "fl": cell["fl"],
            "r": cell["r"],
            "conf": cell["conf"],
            "biome": cell["biome"],
            "s": cell["s"],
            "pop": cell["pop"],
            "culture": cell["culture"],
            "burg": cell["burg"],
            "road": cell["road"],
            "crossroad": cell["crossroad"],
            "state": cell["state"],
            "religion": cell["religion"],
            "province": cell["province"]
        }
        cells_rows.append(row)



# Create data frames from the lists of dictionaries
states_df = pd.DataFrame(states_rows, columns=["i", "name"])
provinces_df = pd.DataFrame(provinces_rows, columns=["i", "state", "center", "burg", "name", "formName", "fullName", "color"])
cultures_df = pd.DataFrame(cultures_rows, columns=["i", "name"])
religion_df = pd.DataFrame(religions_rows, columns=["i", "name", "color", "culture", "type", "form", "deity", "center"])
burgs_df = pd.DataFrame(burgs_rows, columns=["i", "cell", "name", "x", "y"])
cells_df = pd.DataFrame(cells_rows, columns=["i","v", "c","p", "g","h", "area","f", "t", "haven", "harbor","fl", "r","conf", "biome","s", "pop","culture", "burg", "road", "crossroad","state", "religion","province"])

# Save each data frame to a separate sheet in the same Excel file
with pd.ExcelWriter("combined_data.xlsx") as writer:
    states_df.to_excel(writer, sheet_name="states", index=False)
    provinces_df.to_excel(writer, sheet_name="provinces", index=False)
    cultures_df.to_excel(writer, sheet_name="cultures", index=False)
    religion_df.to_excel(writer, sheet_name="religion", index=False)
    burgs_df.to_excel(writer, sheet_name="burgs", index=False)
    cells_df.to_excel(writer, sheet_name="cells", index=False)