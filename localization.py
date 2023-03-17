import os
import pandas as pd
import re

def religionLoc(output_dir):
    # read the combined data file
    data_file = os.path.join(output_dir, "combined_data.xlsx")
    df = pd.read_excel(data_file, sheet_name="religion")

    # create the religions dictionary
    religions = {}
    for i, row in df.iterrows():
        name = row["name"]
        modifiedName = re.sub(r'\W+', '', name).lower()
        religion = {
            "name": name,
            "type": row["type"],
            "form": row["form"],
            "deity": row["deity"]
        }
        religions[modifiedName] = religion

    # Make sure the directory exists
    os.makedirs(os.path.join(output_dir, "localization/english"), exist_ok=True)

    # Make sure the file exists
    yml_file = os.path.join(output_dir, "localization/english/religion_conv_l_english.yml")
    if not os.path.exists(yml_file):
        open(yml_file, "w", encoding="utf-8-sig").close()

    # create the yml file
    yml_file = os.path.join(output_dir, "localization/english/religion_conv_l_english.yml")
    with open(yml_file, "w", encoding="utf-8-sig") as f:
        f.write("l_english:\n\n")
        for key, religion in religions.items():
            name = religion["name"]
            form = religion["form"]
            type = religion["type"]
            deity = religion["deity"]
            # handle empty deity value
            if pd.isna(deity):
                deity_name = ""
            else:
                deity_name = deity.split()[0].replace(",",
                                                      "")  # get the first word of the deity value and remove commas
                if ',' in deity:
                    high_god_name_2 = deity.split(',')[
                        1].strip()  # get the text after the comma and remove leading/trailing spaces
                else:
                    high_god_name_2 = deity_name

            value = re.sub(r'\([^()]*\)', '', name)  # remove any characters inside brackets
            value = re.sub(r'\(|\)', '', value).strip()  # remove brackets and extra space
            value = re.sub(r'\s+', ' ', value)  # replace any double spaces with a single space
            f.write(f" {key}_religion:0 \"{value}\"\n")
            f.write(f" {key}:0 \"{value}\"\n")
            f.write(f" {key}_religion_adj:0 \"{value}\"\n")
            f.write(f" {key}_adj:0 \"{value}\"\n")
            f.write(f" rf_{key}:0 \"{value}\"\n")


            if pd.isna(deity) or deity == "":
                f.write(f" {key}_religion_desc:0 \"{value} is a {form} {type} Belief system, this Belief system has no deity \"\n")
                f.write(f" {key}_high_god_name:0 \"The Spirits\"\n")

            else:
                f.write(f" {key}_religion_desc:0 \"{value} is a {form} {type} religion that believes in {deity} \"\n")
                f.write(f" {key}_high_god_name:0 \"{deity_name}\"\n")
                f.write(f" {key}_high_god_name_2:0 \"{high_god_name_2}\"\n")
                f.write(f" {key}_high_god_name_3:0 \"{deity_name}\"\n")
                f.write(f" {key}_high_god_name_possessive:0 \"{deity_name}'s\"\n")
                f.write(f" {key}_good_god_name_jesus:0 \"{deity_name}\"\n")





            # f.write(f" {key}_religion_desc:0 \"{value} is a {form} {type} religion that believes in {deity} \"\n")


#religionLoc(output_dir)

