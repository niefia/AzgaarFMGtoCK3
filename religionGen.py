import pandas as pd
import os
import random

# Load the Excel file into a pandas DataFrame
file_path = "combined_data.xlsx"
df = pd.read_excel(file_path, sheet_name="religion")

# Create a folder to store the text files
folder_path = "common/religion/religions"
os.makedirs(folder_path, exist_ok=True)

# Loop through the rows of the DataFrame
for index, row in df.iterrows():

    name = row["name"]
    type = row["type"]
    first_word = name.split(" ")[0]
    value = row["origin"]
    reform = ["unreformed_faith_doctrine"]
    paganroots = "no"

    if type == "Folk":
        pagan_roots = "yes"
    else:
        pagan_roots = "no"

    # Check if the value in column i is 0
    if value == 0:
        family = "rf_pagan"
        doc_hostile = random.choice(['pagan_hostility_doctrine', 'abrahamic_hostility_doctrine'])
        doc_hof = random.choice(['doctrine_no_head', 'doctrine_spiritual_head'])
        doc_tolerance = "doctrine_pluralism_pluralistic"
        doc_holdings = "doctrine_theocracy_temporal"
        doc_marriage= random.choice(['doctrine_monogamy', 'doctrine_polygamy', 'doctrine_concubines'])
        doc_divorce = random.choice(['doctrine_divorce_disallowed', 'doctrine_divorce_approval', 'doctrine_divorce_allowed'])
        doctrine_bastardry = random.choice(['doctrine_bastardry_none', 'doctrine_bastardry_legitimization', 'doctrine_bastardry_all'])
        doctrine_homosexuality = "doctrine_homosexuality_accepted"
        doctrine_deviancy = random.choice(['doctrine_deviancy_crime', 'doctrine_deviancy_shunned', 'doctrine_deviancy_accepted'])
        doctrine_adultery_men = random.choice(['doctrine_adultery_men_crime', 'doctrine_adultery_men_shunned', 'doctrine_adultery_men_accepted'])
        doctrine_adultery_women = random.choice(['doctrine_adultery_women_crime', 'doctrine_adultery_women_shunned', 'doctrine_adultery_women_accepted'])
        doctrine_kinslaying = random.choice(['doctrine_kinslaying_any_dynasty_member_crime', 'doctrine_kinslaying_extended_family_crime', 'doctrine_kinslaying_shunned', 'doctrine_kinslaying_close_kin_crime', 'doctrine_kinslaying_accepted,  '])
        doctrine_witchcraft = random.choice(['doctrine_witchcraft_crime', 'doctrine_witchcraft_shunned', 'doctrine_witchcraft_accepted'])
        doctrine_gender = random.choice(['doctrine_gender_male_dominated', 'doctrine_gender_equal', 'doctrine_gender_female_dominated'])
        doctrine_consanguinity = random.choice(['doctrine_consanguinity_restricted', 'doctrine_consanguinity_cousins', 'doctrine_consanguinity_aunt_nephew_and_uncle_niece', 'doctrine_consanguinity_unrestricted'])
        doctrine_pluralism = random.choice(['doctrine_pluralism_fundamentalist', 'doctrine_pluralism_righteous', 'doctrine_pluralism_pluralistic'])
        doctrine_theocracy = random.choice(['doctrine_theocracy_lay_clergy', 'doctrine_theocracy_temporal'])
        doctrine_head_of_faith = random.choice(['doctrine_no_head', 'doctrine_spiritual_head', 'doctrine_temporal_head'])
        doctrine_clerical_function = random.choice(['doctrine_clerical_function_taxation', 'doctrine_clerical_function_alms_and_pacification', 'doctrine_clerical_function_recruitment'])
        doctrine_clerical_gender = random.choice(['doctrine_clerical_gender_male_only', 'doctrine_clerical_gender_female_only', 'doctrine_clerical_gender_either'])
        doctrine_clerical_marriage = random.choice(['doctrine_clerical_marriage_allowed', 'doctrine_clerical_marriage_disallowed'])
        doctrine_clerical_succession = random.choice(['doctrine_clerical_succession_temporal_appointment', 'doctrine_clerical_succession_spiritual_appointment', 'doctrine_clerical_succession_temporal_fixed_appointment','doctrine_clerical_succession_spiritual_fixed_appointment'])

        # Write the name to a text file with "00_" at the start
        file_name = f"00_{first_word}.txt"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "w") as file:
            file.write(f"{first_word}_religion = {{\n\tfamily = rf_{first_word}"
                       f"\n\tdoctrine = {doc_hostile}"
                       f"\n\tpagan_roots = {paganroots}\n"
                       f"\n\tdoctrine = {doctrine_head_of_faith}"
                       f"\n\tdoctrine = {doctrine_gender}"
                       f"\n\tdoctrine = {doctrine_pluralism}"
                       f"\n\tdoctrine = {doctrine_theocracy}"
                       f"\n\tdoctrine = {doc_marriage}"
                       f"\n\tdoctrine = {doc_divorce}"
                       f"\n\tdoctrine = {doctrine_bastardry}"
                       f"\n\tdoctrine = {doctrine_consanguinity}"
                       f"\n\tdoctrine = {doctrine_homosexuality}"
                       f"\n\tdoctrine = {doctrine_adultery_men}"
                       f"\n\tdoctrine = {doctrine_adultery_women}"
                       f"\n\tdoctrine = {doctrine_kinslaying}"
                       f"\n\tdoctrine = {doctrine_deviancy}"
                       f"\n\tdoctrine = {doctrine_witchcraft}"
                       f"\n\tdoctrine = {doctrine_clerical_function}"
                       f"\n\tdoctrine = {doctrine_clerical_gender}"
                       f"\n\tdoctrine = {doctrine_clerical_marriage}"
                       f"\n\tdoctrine = {doctrine_clerical_succession}\n"
                       f"\n\ttraits ="" {\n"
                       f"\t\tvirtues =""{brave just compassionate""}"
                       f"\n\t\tsins =""{\tcraven arbitrary callous""}"
                       f"\n\t""}"
                       f"\n\tcustom_faith_icons ="" {\n"
                       f"\t\tcustom_faith_1 custom_faith_2 custom_faith_3 custom_faith_4 custom_faith_5 custom_faith_6 custom_faith_7 custom_faith_8"
                       f"\n\t""}"      
                       f"\n\tholy_order_names ="" {}\n"
                       f" \n}}")
