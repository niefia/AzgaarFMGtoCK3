import pandas as pd

# Read the Excel file
df = pd.read_excel('religionChildren.xlsx')

# Create an empty list of lists to store the values of "cName"
cName = [[] for _ in range(len(df))]

# Loop through each row
for index, row in df.iterrows():
    # Check if the "children" column value is a string
    if isinstance(row['children'], str):
        # Get the "children" column value as a list of integers
        children = [int(x) for x in row['children'][1:-1].split(',')]

        # Loop through each child_id number in the list
        for child_id in children:
            # Find the matching "i" value in the "i" column
            match = df.loc[df['i'] == child_id]

            # Append the value in the "name" column to the "cName" list for the current row
            cName[index].append(match.iloc[0]['name'])

# Add the "cName" list as a new column to the dataframe
df['cName'] = cName

# Save the updated dataframe to a new Excel file
df.to_excel('religionChildren_cName.xlsx', index=False)
