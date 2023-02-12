import pandas as pd
import os

# Load the Excel file into a pandas DataFrame
file_path = "combined_data.xlsx"
df = pd.read_excel(file_path, sheet_name="religion")

# Create a folder to store the text files
folder_path = "common/religion/religion_families"
os.makedirs(folder_path, exist_ok=True)

# Loop through the rows of the DataFrame
for index, row in df.iterrows():
    name = row["name"]
    first_word = name.split(" ")[0]
    value = row["origin"]

    # Check if the value in column i is 0
    if value == 0:
        # Write the name to a text file with "00_" at the start
        file_name = f"00_{first_word}.txt"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "w") as file:
            file.write(f"rf_{first_word} = {{\n\tgraphical_faith = 'orthodox_gfx' \n\thostility_doctrine = abrahamic_hostility_doctrine\n\tdoctrine_background_icon = core_tenet_banner_christian.dds\n}}")