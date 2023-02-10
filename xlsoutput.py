import pandas as pd
import json

# Load the GeoJSON file into a Python dictionary
with open("output.geojson") as f:
    data = json.load(f)

# Create an empty list to store the features
features = []

# Loop through each feature in the GeoJSON file
for feature in data["features"]:
    # Get the properties of the feature
    properties = feature["properties"]

    # Add the properties of the feature to the list
    features.append(properties)

# Convert the list of features to a dataframe
df = pd.DataFrame(features)

# Rename the columns "state" to "Kingdom" and "province" to "County"
df.rename(columns={'state': 'Kingdom', 'province': 'County', 'religion': 'Religion', 'culture': 'Culture'}, inplace=True)

def hex_to_rgb(hex_color):
    if not hex_color.startswith("#") or len(hex_color) != 7:
        return None
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))


df["color"] = df["color"].astype(str)
df[["red", "green", "blue"]] = df["color"].apply(hex_to_rgb).apply(pd.Series)
df = df.drop("color", axis=1)


# Save the dataframe to an XLS spreadsheet
df.to_excel("provinceDef.xlsx", index=False)
