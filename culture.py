import pandas as pd
import hextorgb
import random
import os


#WIP
def heritage_gen(combined_data, pillars_folder):
    # Read the "culture" sheet of "combined_data.xlsx" into a DataFrame
    df = pd.read_excel(combined_data, sheet_name='cultures')

    # Create the necessary directories if they do not exist
    os.makedirs(pillars_folder, exist_ok=True)

    heritage_txt = os.path.join(pillars_folder,'heritage.txt')
    # Create the text file and write to it
    with open(heritage_txt, 'w') as file:

        # Loop through the rows of the DataFrame
        for index, row in df.iterrows():

            # Check if the "origin" column has a value of 0
            if row['origin'] == 0:
                # Write the heritage name and type to the text file
                file.write(f"heritage_{row['name']} = {{\n\ttype = heritage\n}}\n")


#def language_gen():


def culture_gen(input_file, culture_dir):
    # Open the Excel file and read the 'cultures' sheet
    df = pd.read_excel(input_file, sheet_name='cultures')

    # Get a list of unique names
    names = df['name'].unique()

    # Create the output directory if it doesn't exist
    if not os.path.exists(culture_dir):
        os.makedirs(culture_dir)

    # Loop through the list of unique names
    for name in names:



        color = hextorgb.color_generator()

        ethos = random.choice(
            ['ethos_bellicose', 'ethos_stoic', 'ethos_bureaucratic', 'ethos_spiritual', 'ethos_courtly',
             'ethos_egalitarian', 'ethos_communal'])

        #heritage generation requires heritage generation system

        #language generation requires heritage generation syste and should have a new langauge chance factor

        combat_traditions_options = (
            ['tradition_winter_warriors', 'tradition_forest_fighters', 'tradition_mountaineers', 'tradition_warriors_of_the_dry',
             'tradition_highland_warriors', 'tradition_jungle_warriors', 'tradition_only_the_strong',
             'tradition_warriors_by_merit', 'tradition_warrior_monks', 'tradition_talent_acquisition',
             'tradition_strength_in_numbers', 'tradition_frugal_armorsmiths', 'tradition_malleable_invaders',
             'tradition_quarrelsome', 'tradition_swords_for_hire', 'tradition_reverence_for_veterans', 'tradition_stalwart_defenders',
             'tradition_battlefield_looters','tradition_hit_and_run', 'tradition_stand_and_fight', 'tradition_adaptive_skirmishing', 'tradition_formation_fighting',
             'tradition_horse_breeder', 'tradition_longbow_competitions'])

        societal_traditions_options = (
            ['tradition_xenophilic', 'tradition_chivalry', 'tradition_hard_working',
             'tradition_loyal_soldiers',
             'tradition_pacifism', 'tradition_spartan', 'tradition_diasporic',
             'tradition_vegetarianism', 'tradition_seafaring', 'tradition_storytellers',
             'tradition_music_theory', 'tradition_poetry', 'tradition_fishermen',
             'tradition_mendicant_mystics', 'tradition_warrior_culture', 'tradition_martial_admiration',
             'tradition_philosopher_culture',
             'tradition_welcoming', 'tradition_eye_for_an_eye', 'tradition_zealous_people',
             'tradition_forbearing', 'tradition_equitable',
             'tradition_charitable', 'tradition_modest', 'tradition_practiced_pirates',
             'tradition_life_is_just_a_joke', 'tradition_artisans'])


        realm_traditions_options = (
            ['tradition_court_eunuchs', 'tradition_legalistic', 'tradition_republican_legacy',
             'tradition_hereditary_hierarchy',
             'tradition_esteemed_hospitality', 'tradition_gardening', 'tradition_tribe_unity',
             'tradition_astute_diplomats', 'tradition_collective_lands', 'tradition_female_only_inheritance',
             'tradition_equal_inheritance', 'tradition_metal_craftsmanship', 'tradition_family_entrepreneurship',
             'tradition_wedding_ceremonies', 'tradition_culture_blending', 'tradition_isolationist',
             'tradition_fervent_temple_builders',
             'tradition_agrarian', 'tradition_pastoralists', 'tradition_parochialism',
             'tradition_ruling_caste', 'tradition_staunch_traditionalists',
             'tradition_hill_dwellers', 'tradition_forest_folk', 'tradition_mountain_homes', 'tradition_dryland_dwellers', 'tradition_jungle_dwellers',
             'tradition_wetlanders', 'tradition_hidden_cities',
             'tradition_ancient_miners', 'tradition_castle_keepers', 'tradition_city_keepers', 'tradition_maritime_mercantilism'])

        ritual_traditions_options = (
            ['tradition_monogamous', 'tradition_polygamous', 'tradition_concubines', 'tradition_sacred_mountains',
             'tradition_sacred_groves', 'tradition_culinary_art', 'tradition_festivities',
             'tradition_sorcerous_metallurgy', 'tradition_mystical_ancestors', 'tradition_religion_blending',
             'tradition_religious_patronage', 'tradition_medicinal_plants', 'tradition_sacred_hunts',
             'tradition_faith_bound', 'tradition_by_the_sword', 'tradition_language_scholars', 'tradition_runestones',
             'tradition_merciful_blindings'])


        #Complete traditions list
        traditions_options = combat_traditions_options + societal_traditions_options + realm_traditions_options + ritual_traditions_options


        #Prevent duplicate traditions
        traditions1 = random.choice(traditions_options)
        traditions_options.remove(traditions1)
        traditions2 = random.choice(traditions_options)
        traditions_options.remove(traditions2)
        traditions3 = random.choice(traditions_options)
        traditions_options.remove(traditions3)
        traditions4 = random.choice(traditions_options)

        #namelist = ([])

        coa_gfx = random.choice(['arabic_group_coa_gfx','english_coa_gfx','west_african_group_coa_gfx'])

        building_gfx = random.choice(['african_building_gfx','arabic_group_building_gfx','berber_group_building_gfx','indian_building_gfx','mediterranean_building_gfx','mena_building_gfx','norse_building_gfx','steppe_building_gfx','western_building_gfx','iberian_building_gfx'])

        clothing_gfx = random.choice(['african_clothing_gfx', 'byzantine_clothing_gfx','dde_abbasid_clothing_gfx','dde_hre_clothing_gfx','fp1_norse_clothing_gfx','indian_clothing_gfx','mena_clothing_gfx','mongol_clothing_gfx','northern_clothing_gfx', 'western_clothing_gfx',])

        unit_gfx = random.choice(['eastern_unit_gfx', 'indian_unit_gfx','mena_unit_gfx','mongol_unit_gfx', 'norse_unit_gfx', 'northern_unit_gfx', 'sub_sahran_unit_gfx', 'western_unit_gfx' ])

        ethnicities = (['10 = african','10 = arab','10 = asian','10 = byzantine','10 = caucasian','10 = caucasian_blond','10 = circumpolar', '10 = east_african', '10 = indian', '10 = south_indian', '10 = mediterranean', '10 = slavic'])

        ethnicities1 = random.choice(ethnicities)
        ethnicities2 = random.choice(ethnicities)

        martial = random.choice(['martial_custom_male_only', 'martial_custom_equal', 'martial_custom_female_only'])

        filename = os.path.join(culture_dir, f'{name}.txt')
        with open(filename, 'w') as file:
            # Write the contents to the file
            file.write(f"""{name} = {{
        color = {color}
        ethos = {ethos}
        heritage = heritage_akan
        language = language_kwa
        martial_custom = {martial}
        traditions = {{
            {traditions1}
            {traditions2}
            {traditions3}
            {traditions4}
        }}
        name_list = name_list_akan
        coa_gfx = {coa_gfx}
        building_gfx = {building_gfx}
        clothing_gfx = {clothing_gfx}
        unit_gfx = {unit_gfx}
        ethnicities = {{\n
            {ethnicities1}\n
            {ethnicities2}
            

        }}
    }}""")


#culture_gen('combined_data.xlsx', 'common/culture/cultures')



#WIP
def add_parent_child_names():
    # Read the "religion" sheet of "combined_data.xlsx" into a DataFrame
    df = pd.read_excel('combined_data.xlsx', sheet_name='religion')

    # Replace NaN values in the 'origin' column with 0
    df['origin'] = df['origin'].fillna(0).astype(int)

    # Create a dictionary to store the mapping of origin ids to religion names
    origin_to_name = {}
    for index, row in df.iterrows():
        origin_to_name[index] = row['name']

    # Add new columns to the DataFrame to store the parent and child religion names
    df['parent_name'] = ''
    df['child_name'] = ''
    for i in range(1, 4):  # Add up to 3 levels of descendants
        df[f'descendant_{i}_name'] = ''

    # Iterate through the DataFrame and use the dictionary to add the names of child religions to the parent rows
    for index, row in df.iterrows():
        origin = row['origin']
        if origin != 0:
            parent_name = origin_to_name[origin]
            df.at[origin, 'parent_name'] = parent_name

            # Add child religion name to parent row
            if df.at[origin, 'child_name'] == '':
                df.at[origin, 'child_name'] = row['name']
            else:
                df.at[origin, 'child_name'] += ', ' + row['name']

            # Add descendant religion names to parent row
            for i in range(1, 4):
                if origin in origin_to_name:
                    origin_name = origin_to_name[origin]
                    if df.at[origin, f'descendant_{i}_name'] == '':
                        df.at[origin, f'descendant_{i}_name'] = row['name']
                    else:
                        df.at[origin, f'descendant_{i}_name'] += ', ' + row['name']
                    origin = df.at[origin, 'origin']
                else:
                    break

    # Save the updated DataFrame to a new sheet in the same file
    with pd.ExcelWriter('combined_data.xlsx', engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='parents_religion', index=False)


