import pandas as pd
import os
# Load the first Excel file into a pandas DataFrame
df1 = pd.read_excel('cellsData.xlsx')

# Load the second Excel file into a pandas DataFrame
df2 = pd.read_excel('combined_data.xlsx')

df3 = pd.read_excel('combined_data.xlsx', sheet_name=1)

df4 = pd.read_excel('combined_data.xlsx', sheet_name=2)

df5 = pd.read_excel('combined_data.xlsx', sheet_name=3)

# Create a dictionary from the second DataFrame that maps numbers to names
mapping = dict(zip(df2['i'], df2['name']))
provmapping = dict(zip(df3['i'], df3['name']))
culturemapping = dict(zip(df4['i'], df4['name']))
religionmapping = dict(zip(df5['i'], df5['name']))

# Replace the numbers in the first DataFrame with the associated names
df1['Kingdom'] = df1['Kingdom'].map(mapping)
df1['County'] = df1['County'].map(provmapping)
df1['Religion'] = df1['Religion'].map(religionmapping)


# Save the updated first DataFrame to a new Excel file
df1.to_excel('updated_file.xlsx', index=False)
