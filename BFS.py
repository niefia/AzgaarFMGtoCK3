import pandas as pd
from queue import Queue
import openpyxl
from openpyxl.styles import PatternFill
import random
import hextorgb
import ast
import pandas as pd
from PIL import Image, ImageDraw
from openpyxl import Workbook
import openpyxl
import re
import xlwt
import json


def bfs_distance(combined_data_file, cells_data_file, output_file):
    # Read data from Excel files
    combined_data = pd.read_excel(combined_data_file, sheet_name="burgs")
    cells_data = pd.read_excel(cells_data_file, usecols=["id", "neighbors", "coordinates", "type", "County"])

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
    total_cells = len(cells_data)
    current_cell = 0
    progress = 0
    progress_bar_length = 20
    print("Calculating distances...")
    print("Progress Bar may finish at around 65 as it only counts populated cells ")
    while not frontier.empty():
        current = frontier.get()
        if current in cells_data["id"].tolist() and cells_data.loc[cells_data["id"] == current, "type"].tolist()[
            0] != "ocean":
            for next_cell in cells_data.loc[cells_data["id"] == current, "neighbors"].tolist()[0]:
                if next_cell not in cost_so_far and cells_data.loc[cells_data["id"] == next_cell, "type"].tolist()[
                    0] != "ocean" and cells_data.loc[cells_data["id"] == next_cell, "County"].tolist()[0] == \
                        cells_data.loc[cells_data["id"] == current, "County"].tolist()[0]:
                    cost_so_far[next_cell] = cost_so_far[current] + 1
                    started_at[next_cell] = started_at[current]
                    coordinates[next_cell] = cells_data.loc[cells_data["id"] == next_cell, "coordinates"].tolist()[0]
                    frontier.put(next_cell)
                    # Update progress bar
                    current_cell += 1
                    progress = int(current_cell / total_cells * 100)
                    percent_done = int(progress_bar_length * progress / 100)
                    percent_left = progress_bar_length - percent_done
                    progress_bar = "[" + "#" * percent_done + " " * percent_left + "]"
                    print(f"\r{progress_bar} {progress}%", end='', flush=True)

    # Create a DataFrame to store the results
    output_data = pd.DataFrame(list(cost_so_far.items()), columns=["id", "distance"])

    # Add a column to the output DataFrame for the nearest town and coordinates
    output_data["nearest_town"] = output_data["id"].apply(lambda x: id_to_town[started_at[x]])
    output_data["coordinates"] = output_data["id"].apply(lambda x: coordinates.get(x))

    # Save the output DataFrame to a new Excel file
    output_data.to_excel(output_file, index=False)
    print
















def colorRandomBFS(file_name):
    # Open the Excel file and select the active worksheet
    workbook = openpyxl.load_workbook(file_name)
    worksheet = workbook.active

    # Get the values from the 'nearest_town' column
    values = [cell.value for cell in worksheet['C'][1:]]

    # Find the unique values and assign a random color to each one
    unique_values = list(set(values))
    color_dict = {}
    for value in unique_values:
        color_dict[value] = '{:06x}'.format(random.randint(0, 0xFFFFFF))

    # Rename the column to 'color'
    worksheet.cell(row=1, column=5).value = "color"

    # Add a new column called 'color' and assign each row a color based on its 'nearest_town' value
    for i, value in enumerate(values):
        cell = worksheet.cell(row=i+2, column=5)
        cell.value = color_dict[value]
        cell.fill = PatternFill(start_color=color_dict[value], end_color=color_dict[value], fill_type='solid')

    # Save the updated worksheet to a new sheet called 'Output'
    workbook.save(file_name)

def provinceMapBFS(file_path, scaling_factor,output_folder):
    # read the Excel file
    df = pd.read_excel(file_path)

    # extract coordinates and colors
    coords_str = df['coordinates'].values
    colors_str = df['color'].values
    coords = []
    colors = []
    for coord_str, color_str in zip(coords_str, colors_str):
        coord_list = ast.literal_eval(coord_str)
        coord_list = [[float(x), float(y)] for x, y in coord_list[0]]
        coords.append(coord_list)
        colors.append(color_str)

    # set up image
    width, height = 8192, 4096
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # draw each polygon with scaling factor applied
    for coord, color in zip(coords, colors):

        # calculate the center pixel
        center_px = (width / 2, height / 2)

        # calculate the pixel value for each coordinate, with scaling factor applied and centered at the center_px
        coord_px = [(int(center_px[0] + (x * scaling_factor)),
                     int(center_px[1] - (y * scaling_factor))) for x, y in coord]

        # draw polygon
        rgbcolor = hextorgb.bfs_hex_to_rgb(color)
        draw.polygon(coord_px, fill=rgbcolor, outline=None)

    img.show()
    # save image
    img.save(output_folder)



#BFSbaronyXLS

#Rearrange and extract BFS Data into new provinceDef file (Cell ID is not used in game but used later to get parent cell data on province,state, religion culture etc)
def extractBFS(input_file, output_file):
    # Load the data from the input file into a pandas DataFrame
    df = pd.read_excel(input_file)

    # Filter the DataFrame to only include rows where distance = 0
    df = df[df["distance"] == 0]

    # Convert the color column from hex to rgb and split into separate columns for r, g, and b
    df[["R", "G", "B"]] = df["color"].apply(lambda x: pd.Series(tuple(int(x[i:i+2], 16) for i in (0, 2, 4)) if len(x) == 6 else (pd.NA, pd.NA, pd.NA)))

    # Create a new workbook and worksheet for writing the filtered data to a new Excel file
    wb = Workbook()
    ws = wb.active

    # Write the header row to the worksheet
    header = ["", "", "R", "G", "B", "Nearest Town", "Cell ID"]
    ws.append(header)

    # Write the filtered data to the worksheet
    for row in df.itertuples(index=False):
        ws.append(["", "", row.R, row.G, row.B, row.nearest_town,row.id])

    # Save the new Excel file with the provided output file name
    wb.save(output_file)


#Copy over Town Id's which will be used as Barony id
def BaronyId(input_file, output_file):
    import pandas as pd

    # Load the input file and select the "burgs" sheet
    combined_data = pd.read_excel(input_file, sheet_name="burgs")

    # Load the "provinceDef.xlsx" file
    province_def = pd.read_excel(output_file)

    # Copy the contents of column 0 from the "combined_data" DataFrame to column 1 of the "province_def" DataFrame
    province_def[province_def.columns[1]] = combined_data.iloc[:, 0]

    # Save the updated "province_def" DataFrame to the specified output file
    province_def.to_excel(output_file, index=False)




def ProvData(updated_file_name, province_def_name, output_file_name):
    # Load the two Excel files into Pandas dataframes
    updated_file = pd.read_excel(updated_file_name)
    province_def = pd.read_excel(province_def_name)

    # Merge the two dataframes based on the 'Cell ID' and 'id' columns
    merged = pd.merge(province_def, updated_file, left_on='Cell ID', right_on='id')

    # Replace the 'Cell ID' column with the 'type' column
    merged['Cell ID'] = merged['type']

    # Define the columns to transfer
    columns_to_transfer = ['Cell ID', 'population', 'Kingdom', 'County', 'Culture', 'Religion']

    merged['Religion'] = merged['Religion'].apply(lambda x: x.lower() if isinstance(x, str) else x)

    # Apply re.sub() function to the 'Religion' column
    merged['Religion'] = merged['Religion'].apply(lambda x: re.sub(r'\W+', '', x) if isinstance(x, str) else x)

    # Transfer the columns from updated_file to province_def for the matching rows
    province_def.loc[merged.index, columns_to_transfer] = merged[columns_to_transfer]

    # Save the modified province_def dataframe to the specified output file
    province_def.to_excel(output_file_name, index=False)




def cOrder(file_path):
    import openpyxl

    # Open the Excel file
    wb = openpyxl.load_workbook(file_path)

    # Select the active worksheet
    ws = wb.active

    # Get the column index of the "Religion", "Culture", "County", and "Kingdom" columns
    religion_col_idx = 0
    culture_col_idx = 0
    county_col_idx = 0
    kingdom_col_idx = 0
    for cell in ws[1]:
        if cell.value == "Religion":
            religion_col_idx = cell.column
        elif cell.value == "Culture":
            culture_col_idx = cell.column
        elif cell.value == "County":
            county_col_idx = cell.column
        elif cell.value == "Kingdom":
            kingdom_col_idx = cell.column

    # Move the "Religion", "Culture", "County", and "Kingdom" columns to columns M, N, O, and P, respectively
    if religion_col_idx > 0:
        ws.move_range(
            f"{openpyxl.utils.get_column_letter(religion_col_idx)}1:{openpyxl.utils.get_column_letter(religion_col_idx)}{ws.max_row}",
            cols=2)
    if culture_col_idx > 0:
        ws.move_range(
            f"{openpyxl.utils.get_column_letter(culture_col_idx)}1:{openpyxl.utils.get_column_letter(culture_col_idx)}{ws.max_row}",
            cols=2)
    if county_col_idx > 0:
        ws.move_range(
            f"{openpyxl.utils.get_column_letter(county_col_idx)}1:{openpyxl.utils.get_column_letter(county_col_idx)}{ws.max_row}",
            cols=2)
    if kingdom_col_idx > 0:
        ws.move_range(
            f"{openpyxl.utils.get_column_letter(kingdom_col_idx)}1:{openpyxl.utils.get_column_letter(kingdom_col_idx)}{ws.max_row}",
            cols=1)

    # Save the updated Excel file
    wb.save(file_path)


def finalorder(excel_file_path):
    # Load Excel file into a pandas DataFrame
    df = pd.read_excel(excel_file_path)

    # Check if columns G and H exist by number
    if len(df.columns) > 7:
        # Delete values in columns G and H
        df.iloc[:, [6, 7]] = ""

    # Check if columns J and L exist by number
    if len(df.columns) > 9:
        # Copy values from Column J to Column I
        df.iloc[:, 8] = df.iloc[:, 9]
        # Copy values from Column L to Column K
        df.iloc[:, 10] = df.iloc[:, 11]

    # Save modified DataFrame back to Excel file
    df.to_excel(excel_file_path, index=False)


def convert_xlsx_to_xls(excel_file_path, output_file):
    # Open the input .xlsx file
    wb = openpyxl.load_workbook(excel_file_path)

    # Create a new .xls workbook
    xls_wb = xlwt.Workbook()

    # Copy each worksheet from the .xlsx workbook to the new .xls workbook
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        xls_sheet = xls_wb.add_sheet(sheet_name)

        for row_index, row in enumerate(sheet.iter_rows()):
            for col_index, cell in enumerate(row):
                xls_sheet.write(row_index, col_index, cell.value)

    # Save the new .xls file
    xls_wb.save(output_file)



#provinceMapBFS('path/to/BFSoutput.xlsx', 38,'map_data/provinces.png')



#extractBFS("BFSoutput.xlsx", "provinceDef.xlsx")
#BaronyId("combined_data.xlsx", "provinceDef.xlsx")

#ProvData("updated_file.xlsx", "provinceDef.xlsx", "provinceDef_updated.xlsx")
#cOrder("provinceDef.xlsx")


#convert_xlsx_to_xls('provinceDef.xlsx', 'provinceDef.xls')
