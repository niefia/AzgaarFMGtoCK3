import pandas as pd
from openpyxl import Workbook

#Rearrange and extract BFS Data into new provinceDef file (Cell ID is not used in game but used later to get parent cell data on province,state, religion culture etc)
def extractBFS():
    # Load the data from the BFSoutput.xlsx file into a pandas DataFrame
    df = pd.read_excel("BFSoutput.xlsx")

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

    # Save the new Excel file
    wb.save("provinceDef.xlsx")

#Copy over Town Id's which will be used as Barony id
def BaronyId():
    import pandas as pd

    # Load the "combined_data.xlsx" file and select the "burgs" sheet
    combined_data = pd.read_excel("combined_data.xlsx", sheet_name="burgs")

    # Load the "provinceDef.xlsx" file
    province_def = pd.read_excel("provinceDef.xlsx")

    # Copy the contents of column 0 from the "combined_data" DataFrame to column 1 of the "province_def" DataFrame
    province_def[province_def.columns[1]] = combined_data.iloc[:, 0]

    # Save the updated "province_def" DataFrame to "provinceDef.xlsx"
    province_def.to_excel("provinceDef.xlsx", index=False)

#Uses the Cell ID obtained earlier to assign Province data
def ProvData():
    # Load the two Excel files into Pandas dataframes
    updated_file = pd.read_excel('updated_file.xlsx')
    province_def = pd.read_excel('provinceDef.xlsx')

    # Merge the two dataframes based on the 'Cell ID' and 'id' columns
    merged = pd.merge(province_def, updated_file, left_on='Cell ID', right_on='id')

    # Replace the 'Cell ID' column with the 'type' column
    merged['Cell ID'] = merged['type']

    # Define the columns to transfer
    columns_to_transfer = ['Cell ID', 'population', 'Kingdom', 'County', 'Culture', 'Religion']

    # Transfer the columns from updated_file to province_def for the matching rows
    province_def.loc[merged.index, columns_to_transfer] = merged[columns_to_transfer]

    # Save the modified province_def dataframe to a new Excel file
    province_def.to_excel('provinceDef.xlsx', index=False)


def cOrder():

    # Load the Excel file into a Pandas DataFrame
    df = pd.read_excel('provinceDef.xlsx')

    # Delete the values in column 7
    df.drop(df.columns[6], axis=1, inplace=False)

    # Write the modified DataFrame back to an Excel file
    df.to_excel('provinceDef.xlsx', index=False)


extractBFS()
BaronyId()
ProvData()
cOrder()