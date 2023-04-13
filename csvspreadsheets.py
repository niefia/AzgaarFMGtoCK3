import pandas as pd
import json
import os
import csv

def jsontocsv(output_dir):
    # Load the JSON data
    noemojidir = os.path.join(output_dir, "noemoji.json")
    with open(noemojidir, 'r') as f:
        data = json.load(f)

    # Create a Pandas DataFrame from the 'info' dictionary
    info_df = pd.DataFrame.from_dict(data['info'], orient='index').T

    # Create a Pandas DataFrame from the 'settings' dictionary
    settings_df = pd.DataFrame.from_dict(data['settings'], orient='index').T

    # Create a Pandas DataFrame from the 'coords' dictionary
    coords_df = pd.DataFrame.from_dict(data['coords'], orient='index').T

    # Create a Pandas DataFrame from the 'cells' dictionary
    cells_df = pd.DataFrame(data['cells']['cells'])

    # Extract the "features" list from the JSON data
    features_list = []
    for item in data['cells']['features']:
        if isinstance(item, dict):
            features_list.append(item)

    # Create a Pandas DataFrame from the "features" list
    features_df = pd.DataFrame(features_list)

    # Create a Pandas DataFrame from the 'cells' dictionary
    cultures_df = pd.DataFrame(data['cells']['cultures'])

    burgs_df = pd.DataFrame(data['cells']['burgs'])

    states_df = pd.DataFrame(data['cells']['states'])

    # Extract the "features" list from the JSON data
    provinces_list = []
    for item in data['cells']['provinces']:
        if isinstance(item, dict):
            provinces_list.append(item)

    # Create a Pandas DataFrame from the "features" list
    provinces_df = pd.DataFrame(provinces_list)

    religions_df = pd.DataFrame(data['cells']['religions'])

    rivers_df = pd.DataFrame(data['cells']['rivers'])

    markers_df = pd.DataFrame(data['cells']['markers'])

    # Extract the 'vertices' from the JSON data and create a DataFrame
    vertices_df = pd.DataFrame(data['vertices'])


    biomes_df = pd.DataFrame.from_dict(data['biomes'], orient='index').T

    notes_df = pd.DataFrame(data['notes'])


    # Create a folder to store the CSV files
    folder_name = os.path.join(output_dir, 'temp')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Write each DataFrame to a separate CSV file in the folder
    info_df.to_csv(os.path.join(folder_name, 'info.csv'), index=False)
    settings_df.to_csv(os.path.join(folder_name, 'settings.csv'), index=False)
    coords_df.to_csv(os.path.join(folder_name, 'coords.csv'), index=False)
    cells_df.to_csv(os.path.join(folder_name, 'cells.csv'), index=False)
    features_df.to_csv(os.path.join(folder_name, 'features.csv'), index=False)
    cultures_df.to_csv(os.path.join(folder_name, 'cultures.csv'), index=False)
    burgs_df.to_csv(os.path.join(folder_name, 'burgs.csv'), index=False)
    states_df.to_csv(os.path.join(folder_name, 'states.csv'), index=False)
    provinces_df.to_csv(os.path.join(folder_name, 'provinces.csv'), index=False)
    religions_df.to_csv(os.path.join(folder_name, 'religions.csv'), index=False)
    rivers_df.to_csv(os.path.join(folder_name, 'rivers.csv'), index=False)
    markers_df.to_csv(os.path.join(folder_name, 'markers.csv'), index=False)
    vertices_df.to_csv(os.path.join(folder_name, 'vertices.csv'), index=False)
    biomes_df.to_csv(os.path.join(folder_name, 'biomes.csv'), index=False)
    notes_df.to_csv(os.path.join(folder_name, 'notes.csv'), index=False)


#jsontocsv()

def cellsgeojsontocsv():
    # Open the GeoJSON file and load its contents into a Python object
    with open('data.geojson') as f:
        data = json.load(f)

    # Create a subfolder if it doesn't exist
    if not os.path.exists('temp'):
        os.makedirs('temp')

    # Create a CSV file and write the header row in the subfolder
    with open('temp/geojson_cells.csv', 'w', newline='') as f:
        fieldnames = ['id', 'height', 'biome', 'type', 'population', 'state', 'province', 'culture', 'religion', 'neighbors']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Loop through each feature and extract its properties
        for feature in data['features']:
            properties = feature['properties']

            # Write the properties to a row in the CSV file
            row = {}
            for key in fieldnames:
                if key in properties:
                    row[key] = properties[key]
                else:
                    row[key] = ''
            writer.writerow(row)


#cellsgeojsontocsv()
